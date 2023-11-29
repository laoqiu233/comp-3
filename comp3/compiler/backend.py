from comp3.common.config import IO_READ_ADDRESS, IO_WRITE_ADDRESS
from comp3.common.instructions import (
    DataStubInstruction,
    DataWord,
    InstrStubInstruction,
    Instruction,
    OpCode,
    OperandType,
    Program,
)
from comp3.compiler.ast import (
    AstBackend,
    AstNode,
    FuncCallNode,
    FuncNode,
    GetCharNode,
    IfNode,
    IntLiteralNode,
    LetNode,
    LetVarNode,
    LoadByIdentifierNode,
    LoadByPointerIdentifierNode,
    LoopWhileNode,
    MathNode,
    MultipleExpressionNode,
    PutCharNode,
    SetNode,
    SetPtrNode,
    StrAllocNode,
    StringLiteralNode,
)


class Comp3Backend(AstBackend):
    stub_counter = 0

    def __init__(self, io_read_addr: int = IO_READ_ADDRESS, io_write_addr: int = IO_WRITE_ADDRESS):
        self.stack_identifiers: list[str] = []
        self.program: list[Instruction] = []
        self.string_literals: set[str] = set()
        self.string_buffers: dict[str, int] = {}
        self.io_read_addr = io_read_addr
        self.io_write_addr = io_write_addr

    @classmethod
    def get_stub_id(cls):
        Comp3Backend.stub_counter += 1
        return Comp3Backend.stub_counter

    def visit(self, node: AstNode):
        node.compile(self)

    def visit_multiple_expressions_node(self, node: MultipleExpressionNode):
        for expr in node.expressions:
            expr.compile(self)

    def visit_let_var_node(self, node: LetVarNode):
        node.load_value.compile(self)
        self.program.append(
            Instruction(
                op_code=OpCode.PUSH,
                operand_type=OperandType.NO_OPERAND,
                operand=0,
                comment=f'pushed variable "{node.identifier}" onto stack',
            )
        )
        self.stack_identifiers.append(node.identifier)

    def visit_let_node(self, node: LetNode):
        for var in node.var_nodes:
            var.compile(self)

        for body_expr in node.body:
            body_expr.compile(self)

        for var in node.var_nodes[::-1]:
            if self.stack_identifiers[-1] != var.identifier:
                raise ValueError(
                    "DEBUG: Stack pop identifiers did not match, this should not happen"
                )
            self.stack_identifiers.pop()
            self.program.append(
                Instruction(
                    op_code=OpCode.POP,
                    operand_type=OperandType.NO_OPERAND,
                    operand=0,
                    comment=f'popped variable "{var.identifier}" out of stack',
                )
            )

    def visit_set_node(self, node: SetNode):
        node.load_value.compile(self)

        if node.identifier in self.stack_identifiers:
            self.program.append(
                Instruction(
                    op_code=OpCode.ST,
                    operand_type=OperandType.STACK_OFFSET,
                    operand=self.stack_identifiers[::-1].index(node.identifier),
                    comment=f"update variable {node.identifier}",
                )
            )
        else:
            self.program.append(
                DataStubInstruction(
                    op_code=OpCode.ST,
                    operand_type=OperandType.ADDRESS,
                    operand=0,
                    comment=f"update global variable {node.identifier}",
                    data_stub_identifier=node.identifier,
                )
            )

    def visit_set_ptr_node(self, node: SetPtrNode):
        node.load_value.compile(self)

        if node.identifier in self.stack_identifiers:
            self.program.append(
                Instruction(
                    op_code=OpCode.ST,
                    operand_type=OperandType.POINTER_STACK_OFFSET,
                    operand=self.stack_identifiers[::-1].index(node.identifier),
                    comment=f"update by pointer {node.identifier}",
                )
            )
        else:
            self.program.append(
                DataStubInstruction(
                    op_code=OpCode.ST,
                    operand_type=OperandType.POINTER_ADDRESS,
                    operand=0,
                    comment=f"update by global pointer {node.identifier}",
                    data_stub_identifier=node.identifier,
                )
            )

    def visit_loop_while_node(self, node: LoopWhileNode):
        start_id = Comp3Backend.get_stub_id()
        end_id = Comp3Backend.get_stub_id()

        loop_condition_index = len(self.program)
        node.loop_condition.compile(self)
        self.program[loop_condition_index].instr_id.append(start_id)

        self.program.append(
            Instruction(
                op_code=OpCode.CMP,
                operand_type=OperandType.IMMEDIATE,
                operand=0,
                comment="check if false",
            )
        )

        self.program.append(
            InstrStubInstruction(
                op_code=OpCode.JZ,
                operand_type=OperandType.ADDRESS,
                operand=0,
                referenced_instr_id=end_id,
                referenced_instr_offset=1,
                comment="end while loop",
            )
        )

        for body_expr in node.body:
            body_expr.compile(self)

        self.program.append(
            InstrStubInstruction(
                op_code=OpCode.JMP,
                operand_type=OperandType.ADDRESS,
                operand=0,
                instr_id=[end_id],
                referenced_instr_id=start_id,
                referenced_instr_offset=0,
                comment="jump to while loop condition check",
            )
        )

    def visit_math_node(self, node: MathNode):
        math_to_op_code = {
            MathNode.MathOp.ADD: OpCode.ADD,
            MathNode.MathOp.SUB: OpCode.SUB,
            MathNode.MathOp.AND: OpCode.AND,
            MathNode.MathOp.OR: OpCode.OR,
            MathNode.MathOp.SHL: OpCode.SHL,
            MathNode.MathOp.SHR: OpCode.SHR,
        }
        branch_to_op_code = {
            MathNode.MathOp.EQ: OpCode.JZ,
            MathNode.MathOp.NE: OpCode.JNZ,
            MathNode.MathOp.LT: OpCode.JB,
            MathNode.MathOp.LE: OpCode.JBE,
            MathNode.MathOp.GT: OpCode.JA,
            MathNode.MathOp.GE: OpCode.JAE,
        }

        end_stub_id = Comp3Backend.get_stub_id()

        # Right operand is processed first only for
        # the left operand to be in AC, and right operand
        # will come from the stack
        node.right_operand.compile(self)  # Right operand in AC
        self.program.append(
            Instruction(
                op_code=OpCode.PUSH,
                operand_type=OperandType.NO_OPERAND,
                operand=0,
                comment=f"push right operand of {node.op} to stack",
            )
        )  # Now right operand is on top of the stack
        self.stack_identifiers.append(
            ""
        )  # Anonymous identifier, probably won't be used by anyone, I hope.
        node.left_operand.compile(self)  # Left operand in AC

        if node.op in math_to_op_code:
            self.program.append(
                Instruction(
                    op_code=math_to_op_code[node.op],
                    operand_type=OperandType.STACK_OFFSET,
                    operand=0,
                    comment=f"do {node.op} math operation",
                )
            )
        else:
            self.program.append(
                Instruction(
                    op_code=OpCode.CMP,
                    operand_type=OperandType.STACK_OFFSET,
                    operand=0,
                    comment=f"do {node.op} comparison",
                )
            )

            self.program.append(
                Instruction(
                    op_code=OpCode.LD,
                    operand_type=OperandType.IMMEDIATE,
                    operand=1,
                    comment="load true value",
                )
            )

            self.program.append(
                InstrStubInstruction(
                    op_code=branch_to_op_code[node.op],
                    operand_type=OperandType.ADDRESS,
                    operand=0,
                    referenced_instr_id=end_stub_id,
                    referenced_instr_offset=0,
                    comment=f"jump to return if {node.op} was success",
                )
            )

            self.program.append(
                Instruction(
                    op_code=OpCode.LD,
                    operand_type=OperandType.IMMEDIATE,
                    operand=0,
                    comment="load false value",
                )
            )

        # Remove right operand from stack
        self.program.append(
            Instruction(
                op_code=OpCode.POP,
                operand_type=OperandType.NO_OPERAND,
                operand=0,
                instr_id=[end_stub_id],
                comment=f"pop right operand of {node.op} from stack",
            )
        )

        if self.stack_identifiers.pop() != "":
            raise ValueError("DEBUG: Stack pop identifiers did not match, this should not happen")

    def visit_get_char_node(self, node: GetCharNode):
        self.program.append(
            Instruction(
                op_code=OpCode.LD,
                operand_type=OperandType.ADDRESS,
                operand=self.io_read_addr,
                comment="io read",
            )
        )

    def visit_put_char_node(self, node: PutCharNode):
        node.load_value.compile(self)
        self.program.append(
            Instruction(
                op_code=OpCode.ST,
                operand_type=OperandType.ADDRESS,
                operand=self.io_write_addr,
                comment="io write",
            )
        )

    def visit_int_literal_node(self, node: IntLiteralNode):
        self.program.append(
            Instruction(
                op_code=OpCode.LD,
                operand_type=OperandType.IMMEDIATE,
                operand=node.value,
                comment=f"load literal {node.value}",
            )
        )

    def visit_load_by_identifier_node(self, node: LoadByIdentifierNode):
        if node.identifier in self.stack_identifiers:
            self.program.append(
                Instruction(
                    op_code=OpCode.LD,
                    operand_type=OperandType.STACK_OFFSET,
                    operand=self.stack_identifiers[::-1].index(node.identifier),
                    comment=f"load by identifier {node.identifier} from stack",
                )
            )
        else:
            self.program.append(
                DataStubInstruction(
                    op_code=OpCode.LD,
                    operand_type=OperandType.IMMEDIATE,
                    operand=0,
                    data_stub_identifier=node.identifier,
                    comment=f"load by identifier {node.identifier} from memory",
                )
            )

    def visit_load_by_pointer_identifier_node(self, node: LoadByPointerIdentifierNode):
        if node.identifier in self.stack_identifiers:
            self.program.append(
                Instruction(
                    op_code=OpCode.LD,
                    operand_type=OperandType.POINTER_STACK_OFFSET,
                    operand=self.stack_identifiers[::-1].index(node.identifier),
                    comment=f"load by pointer {node.identifier}",
                )
            )
        else:
            self.program.append(
                DataStubInstruction(
                    op_code=OpCode.LD,
                    operand_type=OperandType.ADDRESS,
                    operand=0,
                    data_stub_identifier=node.identifier,
                    comment=f"load by global pointer {node.identifier}",
                )
            )

    def visit_func_node(self, node: FuncNode):
        # Function declaration are always in global scope,
        # it's okay to assume that stack_identifiers is empty
        # and the stack is populated by the caller, consisting of
        # the return address and the parameters passed

        # Ret address should be on top of stack
        self.stack_identifiers.append("")

        for param_id in node.param_identifiers:
            self.stack_identifiers.append(param_id)

        func_start_index = len(self.program)

        for body_expr in node.body:
            body_expr.compile(self)

        self.program.append(
            Instruction(
                op_code=OpCode.JMP,
                operand_type=OperandType.POINTER_STACK_OFFSET,
                operand=len(self.stack_identifiers) - 1,
                comment=f"return from function {node.identifier}",
            )
        )

        for param_id in node.param_identifiers[::-1]:
            if self.stack_identifiers.pop() != param_id:
                raise ValueError(
                    "DEBUG: Stack pop identifiers did not match, this should not happen"
                )

        self.program[func_start_index].instr_id.append(node.identifier)

    def visit_func_call_node(self, node: FuncCallNode):
        return_stub_id = Comp3Backend.get_stub_id()

        self.program.append(
            InstrStubInstruction(
                op_code=OpCode.LD,
                operand_type=OperandType.IMMEDIATE,
                operand=0,
                referenced_instr_id=return_stub_id,
                referenced_instr_offset=1,
                comment=f"load next instruction address (return from {node.func_identifier})",
            )
        )
        self.program.append(
            Instruction(
                op_code=OpCode.PUSH,
                operand_type=OperandType.NO_OPERAND,
                operand=0,
                comment="push return address onto the stack",
            )
        )
        self.stack_identifiers.append(
            " ret_address"
        )  # Return address pushed onto the stack, should be anonymous

        for index, param in enumerate(node.params):
            param.compile(self)
            self.program.append(
                Instruction(
                    op_code=OpCode.PUSH,
                    operand_type=OperandType.NO_OPERAND,
                    operand=0,
                    comment=f"push parameter {index} onto stack",
                )
            )
            self.stack_identifiers.append("")  # Param is pushed onto the stack, should be anonymous

        self.program.append(
            InstrStubInstruction(
                op_code=OpCode.JMP,
                operand_type=OperandType.ADDRESS,
                operand=0,
                instr_id=[return_stub_id],
                referenced_instr_id=node.func_identifier,
                referenced_instr_offset=0,
                comment="function call",
            )
        )

        for index, param in reversed(list(enumerate(node.params))):
            self.program.append(
                Instruction(
                    op_code=OpCode.POP,
                    operand_type=OperandType.NO_OPERAND,
                    operand=0,
                    comment=f"pop parameter {index} from stack",
                )
            )
            if self.stack_identifiers.pop() != "":
                raise ValueError(
                    "DEBUG: Stack pop identifiers did not match, this should not happen"
                )

        self.program.append(
            Instruction(
                op_code=OpCode.POP,
                operand_type=OperandType.NO_OPERAND,
                operand=0,
                comment="pop return address from stack",
            )
        )
        if self.stack_identifiers.pop() != " ret_address":
            raise ValueError("DEBUG: Stack pop identifiers did not match, this should not happen")

    def visit_string_literal_node(self, node: StringLiteralNode):
        self.string_literals.add(node.value)

        self.program.append(
            DataStubInstruction(
                op_code=OpCode.LD,
                operand_type=OperandType.IMMEDIATE,
                operand=0,
                data_stub_identifier=node.value,
                comment=f"load string literal {node.value} address",
            )
        )

    def visit_str_alloc_node(self, node: StrAllocNode):
        if node.identifier in self.string_buffers:
            raise ValueError(
                f"Invalid string buffer declaration at line {node.start_token.line} col"
                f" {node.start_token.pos}, identifier {node.identifier} was already declared"
                " previously"
            )

        self.string_buffers[node.identifier] = node.size

    def visit_if_node(self, node: IfNode):
        false_expr_stub_id = Comp3Backend.get_stub_id()
        if_end_stub = Comp3Backend.get_stub_id()
        node.if_condition.compile(self)

        self.program.append(
            Instruction(
                op_code=OpCode.CMP,
                operand_type=OperandType.IMMEDIATE,
                operand=0,
                comment="if compare",
            )
        )
        self.program.append(
            InstrStubInstruction(
                op_code=OpCode.JZ,
                operand_type=OperandType.ADDRESS,
                operand=0,
                referenced_instr_id=(
                    if_end_stub if node.false_expr is None else false_expr_stub_id
                ),
                referenced_instr_offset=(1 if node.false_expr is None else 0),
                comment="jump to end or false branch if false",
            )
        )
        node.true_expr.compile(self)

        if node.false_expr is not None:
            self.program.append(
                InstrStubInstruction(
                    op_code=OpCode.JMP,
                    operand_type=OperandType.ADDRESS,
                    operand=0,
                    referenced_instr_id=if_end_stub,
                    referenced_instr_offset=1,
                    comment="true branch finished, jump to end",
                )
            )

            next_instr_index = len(self.program)
            node.false_expr.compile(self)
            self.program[next_instr_index].instr_id.append(false_expr_stub_id)

        self.program[-1].instr_id.append(if_end_stub)


def replace_stubs(program: Program):
    instr_id_address: dict[int | str, int] = {}
    data_id_address: dict[str, int] = {}

    for index, instr in enumerate(program.instructions):
        for instr_id in instr.instr_id:
            instr_id_address[instr_id] = index

    for index, data in enumerate(program.data_memory):
        if data.identifier is not None:
            data_id_address[data.identifier] = index

    for index, instr in enumerate(program.instructions):
        if isinstance(instr, InstrStubInstruction):
            if instr.referenced_instr_id not in instr_id_address:
                raise ValueError(
                    f"Instruction stub identifier {instr.referenced_instr_id} in instruction"
                    f" {index} was not found in compiled program"
                )
            referenced_addr = (
                instr_id_address[instr.referenced_instr_id] + instr.referenced_instr_offset
            )
            program.instructions[index] = Instruction(
                op_code=instr.op_code,
                operand_type=instr.operand_type,
                operand=referenced_addr,
                comment=instr.comment,
            )
        elif isinstance(instr, DataStubInstruction):
            if instr.data_stub_identifier not in data_id_address:
                raise ValueError(
                    f"Data stub identifier {instr.data_stub_identifier} in instruction {index} was"
                    " not found in compiled program"
                )
            program.instructions[index] = Instruction(
                op_code=instr.op_code,
                operand_type=instr.operand_type,
                operand=data_id_address[instr.data_stub_identifier],
                comment=instr.comment,
            )


def is_global(node: AstNode) -> bool:
    return isinstance(node, (FuncNode, StrAllocNode))


def index_instructions(program: Program):
    for index, instr in enumerate(program.instructions):
        instr.instr_index = index


class CompilerFacade:
    def __init__(self):
        self.instructions: list[Instruction] = []
        self.string_literals: set[str] = set()
        self.string_buffers: dict[str, int] = {}

    def process_backend_results(self, backend: Comp3Backend):
        self.instructions += backend.program
        for literal in backend.string_literals:
            self.string_literals.add(literal)
        for identifier, size in backend.string_buffers.items():
            if identifier in self.string_buffers:
                raise ValueError(
                    f"String buffer identifier {identifier} was declared more than one time"
                )
            self.string_buffers[identifier] = size

    def build_data_memory(self) -> list[DataWord]:
        data_memory: list[DataWord] = []

        for literal in self.string_literals:
            literal_addr = len(data_memory)
            for char in literal:
                data_memory.append(DataWord(value=ord(char)))
            # C-string end
            data_memory.append(DataWord(value=0))
            data_memory[literal_addr].identifier = literal

        for buffer_identifier, size in self.string_buffers.items():
            buffer_addr = len(data_memory)
            for _ in range(size):
                data_memory.append(DataWord(value=0))
            data_memory[buffer_addr].identifier = buffer_identifier

        return data_memory

    def build_program(self, nodes: list[AstNode]):
        # Process all global declarations first
        for node in filter(is_global, nodes):
            backend = Comp3Backend()
            backend.visit(node)
            self.process_backend_results(backend)

        program_start = len(self.instructions)

        # Process everything else
        for node in filter(lambda x: not is_global(x), nodes):
            backend = Comp3Backend()
            backend.visit(node)
            self.process_backend_results(backend)

        self.instructions.append(
            Instruction(op_code=OpCode.HLT, operand_type=OperandType.NO_OPERAND, operand=0)
        )

        data_memory = self.build_data_memory()

        program = Program(
            start_addr=program_start, instructions=self.instructions, data_memory=data_memory
        )
        replace_stubs(program)
        index_instructions(program)

        return program


def build_program_from_nodes(nodes: list[AstNode]) -> Program:
    facade = CompilerFacade()
    return facade.build_program(nodes)
