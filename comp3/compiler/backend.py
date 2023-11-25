from comp3.compiler.ast import AstBackend, AstNode, GetCharNode, IntLiteralNode, LetNode, LetVarNode, LoadByIdentifierNode, LoopWhileNode, MathNode, PutCharNode, SetNode
from comp3.common.instructions import OpCode, OperandType, Instruction, DataStubInstruction, InstrStubInstruction, Program

class Comp3Backend(AstBackend):
    stub_counter = 0

    def __init__(self, io_read_addr: int = 69, io_write_addr: int = 42):
        self.stack_identifiers: list[str] = []
        self.program: list[Instruction] = []
        self.io_read_addr = io_read_addr
        self.io_write_addr = io_write_addr

    @classmethod
    def get_stub_id(cls):
        Comp3Backend.stub_counter += 1
        return Comp3Backend.stub_counter

    def visit(self, node: AstNode):
        node.compile(self)

    def visit_let_var_node(self, node: LetVarNode):
        node.load_value.compile(self)
        self.program.append(Instruction(
            op_code=OpCode.PUSH,
            operand_type=OperandType.NO_OPERAND,
            operand=0
        ))
        self.stack_identifiers.append(node.identifier)

    def visit_let_node(self, node: LetNode):
        for var in node.vars:
            var.compile(self)

        for body_expr in node.body:
            body_expr.compile(self)

        for var in node.vars[::-1]:
            if self.stack_identifiers[-1] != var.identifier:
                raise ValueError(f'DEBUG: Stack pop identifiers did not match, this should not happen')
            self.stack_identifiers.pop()
            self.program.append(Instruction(
                op_code=OpCode.POP,
                operand_type=OperandType.NO_OPERAND,
                operand=0
            ))

    def visit_set_node(self, node: SetNode):
        node.load_value.compile(self)

        if node.identifier in self.stack_identifiers:
            self.program.append(Instruction(
                op_code=OpCode.ST,
                operand_type=OperandType.STACK_OFFSET,
                operand=self.stack_identifiers[::-1].index(node.identifier)+1
            ))
        else:
            raise ValueError(f'Unkonwn identifier {node.identifier} found at line {node.start_token.line} col {node.start_token.pos}')
        
    def visit_loop_while_node(self, node: LoopWhileNode):
        start_id = Comp3Backend.get_stub_id()
        end_id = Comp3Backend.get_stub_id()

        loop_condition_index = len(self.program)
        node.loop_condition.compile(self)
        self.program[loop_condition_index].instr_id = start_id

        self.program.append(InstrStubInstruction(
            op_code=OpCode.JZ,
            operand_type=OperandType.ADDRESS,
            operand=0,
            referenced_instr_id=end_id,
            referenced_instr_offset=0
        ))

        for body_expr in node.body:
            body_expr.compile(self)

        self.program.append(InstrStubInstruction(
            op_code=OpCode.JMP,
            operand_type=OperandType.ADDRESS,
            operand=0,
            instr_id=end_id,
            referenced_instr_id=start_id,
            referenced_instr_offset=0
        ))
        
    def visit_math_node(self, node: MathNode):
        math_to_op_code = {
            MathNode.MathOp.ADD: OpCode.ADD,
            MathNode.MathOp.SUB: OpCode.SUB,
            MathNode.MathOp.AND: OpCode.AND,
            MathNode.MathOp.OR:  OpCode.OR
        }
        branch_to_op_code = {
            MathNode.MathOp.EQ: OpCode.JZ,
            MathNode.MathOp.NE: OpCode.JNZ,
            MathNode.MathOp.LT: OpCode.JB,
            MathNode.MathOp.LE: OpCode.JBE,
            MathNode.MathOp.GT: OpCode.JA,
            MathNode.MathOp.GE: OpCode.JAE
        }

        end_stub_id = Comp3Backend.get_stub_id()

        # Right operand is processed first only for
        # the left operand to be in AC, and right operand 
        # will come from the stack
        node.right_operand.compile(self) # Right operand in AC
        self.program.append(Instruction(
            op_code=OpCode.PUSH,
            operand_type=OperandType.NO_OPERAND,
            operand=0
        )) # Now right operand is on top of the stack
        self.stack_identifiers.append('') # Anonymous identifier, probably won't be used by anyone, I hope.
        node.left_operand.compile(self) # Left operand in AC

        if node.op in math_to_op_code:
            self.program.append(Instruction(
                op_code=math_to_op_code[node.op],
                operand_type=OperandType.STACK_OFFSET,
                operand=1
            ))
        else:
            self.program.append(Instruction(
                op_code=OpCode.CMP,
                operand_type=OperandType.STACK_OFFSET,
                operand=1
            ))

            self.program.append(Instruction(
                op_code=OpCode.LD,
                operand_type=OperandType.IMMEDIATE,
                operand=1
            ))

            self.program.append(InstrStubInstruction(
                op_code=branch_to_op_code[node.op],
                operand_type=OperandType.ADDRESS,
                operand=0,
                referenced_instr_id=end_stub_id,
                referenced_instr_offset=0
            ))

            self.program.append(Instruction(
                op_code=OpCode.LD,
                operand_type=OperandType.IMMEDIATE,
                operand=0,
            ))

        # Remove right operand from stack
        self.program.append(Instruction(
            op_code=OpCode.POP,
            operand_type=OperandType.NO_OPERAND,
            operand=0,
            instr_id=end_stub_id
        ))

        if self.stack_identifiers.pop() != '':
            raise ValueError(f'DEBUG: Stack pop identifiers did not match, this should not happen')

    def visit_get_char_node(self, node: GetCharNode):
        self.program.append(Instruction(
            op_code=OpCode.LD,
            operand_type=OperandType.ADDRESS,
            operand=self.io_read_addr
        ))

    def visit_put_char_node(self, node: PutCharNode):
        node.load_value.compile(self)
        self.program.append(Instruction(
            op_code=OpCode.ST,
            operand_type=OperandType.ADDRESS,
            operand=self.io_write_addr
        ))

    def visit_int_literal_node(self, node: IntLiteralNode):
        self.program.append(Instruction(
            op_code=OpCode.LD,
            operand_type=OperandType.IMMEDIATE,
            operand=node.value
        ))

    def visit_load_by_identifier_node(self, node: LoadByIdentifierNode):
        if node.identifier in self.stack_identifiers:
            self.program.append(Instruction(
                op_code=OpCode.LD,
                operand_type=OperandType.STACK_OFFSET,
                operand=self.stack_identifiers[::-1].index(node.identifier)+1
            ))

def replace_stubs(program: Program):
    instr_id_address: dict[int, int] = {}

    for index, instr in enumerate(program.instructions):
        if instr.instr_id is not None:
            instr_id_address[instr.instr_id] = index

    for i in range(len(program.instructions)):
        instr = program.instructions[i]
        if isinstance(instr, InstrStubInstruction):
            referenced_addr = instr_id_address[instr.referenced_instr_id] + instr.referenced_instr_offset
            program.instructions[i] = Instruction(
                op_code = program.instructions[i].op_code,
                operand_type = program.instructions[i].operand_type,
                operand = referenced_addr
            )
    