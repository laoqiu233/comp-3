from dataclasses import dataclass, field
from typing import Optional

from comp3.common.config import IO_READ_ADDRESS, IO_WRITE_ADDRESS
from comp3.common.instructions import AluOp, OpCode, OperandType
from comp3.machine.common import AluLopSel, AluRopSel, BrMuxSel, DataIoMuxSel, DrMuxSel
from comp3.machine.datapath import DataPath


# pylint: disable=too-many-instance-attributes
@dataclass
class MicroCode:
    """-
    In Python, we must first dispatch all
    select signals then move on to latching.
    In real life it's okay to simultaniously
    dispatch the signals, since everything
    should stabilize during the execution
    cycle for this microcode.
    """

    alu_lop_sel: AluLopSel = AluLopSel.SEL_ZERO
    alu_rop_sel: AluRopSel = AluRopSel.SEL_ZERO
    data_io_mux_sel: DataIoMuxSel = DataIoMuxSel.SEL_DATA
    br_mux_sel: BrMuxSel = BrMuxSel.SEL_ALU
    dr_mux_sel: DrMuxSel = DrMuxSel.SEL_DATA
    alu_op: AluOp = AluOp.ADD

    latch_ac: bool = False
    latch_br: bool = False
    latch_ir: bool = False
    latch_dr: bool = False
    latch_ar: bool = False
    latch_sp: bool = False
    latch_pc: bool = False
    latch_io: bool = False
    latch_data: bool = False
    latch_ps: bool = False
    latch_hlt: bool = False

    alias: Optional[str] = None

    def execute(self, data_path: DataPath):
        data_path.sel_alu_lop(self.alu_lop_sel)
        data_path.sel_alu_rop(self.alu_rop_sel)
        data_path.sel_data_io_mux(self.data_io_mux_sel)
        data_path.sel_br_mux(self.br_mux_sel)
        data_path.sel_dr_mux(self.dr_mux_sel)
        data_path.sel_alu_op(self.alu_op)

        if self.latch_ac:
            data_path.latch_ac()
        if self.latch_br:
            data_path.latch_br()
        if self.latch_ir:
            data_path.latch_ir()
        if self.latch_dr:
            data_path.latch_dr()
        if self.latch_ar:
            data_path.latch_ar()
        if self.latch_sp:
            data_path.latch_sp()
        if self.latch_pc:
            data_path.latch_pc()
        if self.latch_io:
            data_path.write_io()
        if self.latch_data:
            data_path.write_data()
        if self.latch_ps:
            data_path.latch_ps()
        if self.latch_hlt:
            data_path.latch_hlt()

    def _format_dr(self) -> str:
        if self.dr_mux_sel == DrMuxSel.SEL_ALU:
            return f"DR <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "
        if self.dr_mux_sel == DrMuxSel.SEL_DATA:
            return f"DR <- {self.data_io_mux_sel} "
        return ""

    def _format_br(self) -> str:
        if self.br_mux_sel == BrMuxSel.SEL_ALU:
            return f"BR <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "
        if self.br_mux_sel == BrMuxSel.SEL_PC:
            return "BR <- PC "
        return ""

    def __str__(self) -> str:
        s = ""

        if self.latch_ac:
            s += f"AC <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_br:
            s += self._format_br()

        if self.latch_ir:
            s += "IR <- INSTR_MEMORY "

        if self.latch_dr:
            s += self._format_dr()

        if self.latch_ar:
            s += f"AR <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_sp:
            s += f"SP <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_pc:
            s += f"PC <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_ps:
            s += f"PS <- NZC({self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel}) "

        if self.latch_io:
            s += f"IO <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_data:
            s += f"DATA <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_hlt:
            s += "HLT "

        if self.alias is not None:
            s += f"({self.alias})"

        return s


@dataclass
class BranchingMicroCode:
    """
    Branching in COMP-3 microcode works as an
    AND formula for all the check parameters.
    The parameters marked as None are not included in
    the logical AND.
    If the result is True, then perform the jump,
    otherwise continue executing.
    """

    branch_target: int | str  # Micro code address or alias

    check_op_code: list[OpCode] = field(default_factory=list)
    check_operand_type: list[OperandType] = field(default_factory=list)
    check_operand: Optional[int] = None
    check_c_flag: Optional[bool] = None
    check_n_flag: Optional[bool] = None
    check_z_flag: Optional[bool] = None

    alias: Optional[str] = None

    def execute(self, datapath: DataPath) -> bool:
        res = True

        if (
            len(self.check_op_code) != 0
            and datapath.ir.get_instruction().op_code not in self.check_op_code
        ):
            res = False

        if (
            len(self.check_operand_type) != 0
            and datapath.ir.get_instruction().operand_type not in self.check_operand_type
        ):
            res = False

        if (
            self.check_operand is not None
            and datapath.ir.get_instruction().operand != self.check_operand
        ):
            res = False

        if self.check_c_flag is not None and datapath.ps.c != self.check_c_flag:
            res = False

        if self.check_n_flag is not None and datapath.ps.n != self.check_n_flag:
            res = False

        if self.check_z_flag is not None and datapath.ps.z != self.check_z_flag:
            res = False

        return res

    def __str__(self) -> str:
        s = f"JUMP TO {self.branch_target} IF "

        if len(self.check_op_code) != 0:
            s += f"OP_CODE IN {list(map(lambda x: x.value, self.check_op_code))} "

        if len(self.check_operand_type) != 0:
            s += f"OPERNAD_TYPE IN {list(map(lambda x: x.value, self.check_operand_type))} "

        if self.check_operand is not None:
            s += f"OPERAND = {self.check_operand} "

        if self.check_c_flag is not None:
            s += f"C = {self.check_c_flag} "

        if self.check_n_flag is not None:
            s += f"N = {self.check_n_flag} "

        if self.check_z_flag is not None:
            s += f"Z = {self.check_z_flag} "

        if self.alias is not None:
            s += f"({self.alias})"

        return s


runtime: list[MicroCode | BranchingMicroCode] = [
    MicroCode(latch_ir=True, alias="start"),
    MicroCode(br_mux_sel=BrMuxSel.SEL_PC, latch_br=True),
    MicroCode(alu_lop_sel=AluLopSel.SEL_BR, alu_op=AluOp.INC, latch_pc=True),
    BranchingMicroCode("push", check_op_code=[OpCode.PUSH]),
    BranchingMicroCode("pop", check_op_code=[OpCode.POP]),
    BranchingMicroCode("hlt", check_op_code=[OpCode.HLT]),
    BranchingMicroCode("fetch_pointer_address", check_operand_type=[OperandType.POINTER_ADDRESS]),
    BranchingMicroCode(
        "fetch_stack_offset",
        check_operand_type=[OperandType.STACK_OFFSET, OperandType.POINTER_STACK_OFFSET],
    ),
    MicroCode(
        alu_lop_sel=AluLopSel.SEL_IR,
        dr_mux_sel=DrMuxSel.SEL_ALU,
        latch_dr=True,
        alias="fetch_immediate_or_no_operand_or_address",
    ),
    BranchingMicroCode("fetch_operand", check_operand_type=[OperandType.ADDRESS]),
    BranchingMicroCode("execute"),
    MicroCode(alu_lop_sel=AluLopSel.SEL_IR, latch_ar=True, alias="fetch_pointer_address"),
    MicroCode(latch_dr=True),
    BranchingMicroCode("fetch_operand"),
    MicroCode(
        alu_lop_sel=AluLopSel.SEL_IR,
        alu_rop_sel=AluRopSel.SEL_SP,
        dr_mux_sel=DrMuxSel.SEL_ALU,
        latch_dr=True,
        alias="fetch_stack_offset",
    ),
    BranchingMicroCode("fetch_operand", check_operand_type=[OperandType.STACK_OFFSET]),
    MicroCode(alu_rop_sel=AluRopSel.SEL_DR, latch_ar=True),
    MicroCode(latch_dr=True),
    MicroCode(alu_rop_sel=AluRopSel.SEL_DR, latch_ar=True, alias="fetch_operand"),
    BranchingMicroCode(
        "jump_routing",
        check_op_code=[
            OpCode.JZ,
            OpCode.JNZ,
            OpCode.JB,
            OpCode.JBE,
            OpCode.JA,
            OpCode.JAE,
            OpCode.JMP,
        ],
        alias="execute",
    ),
    BranchingMicroCode("st", check_op_code=[OpCode.ST]),
    BranchingMicroCode(
        "execute2", check_operand_type=[OperandType.IMMEDIATE, OperandType.NO_OPERAND]
    ),
    BranchingMicroCode(
        "fetch_from_io", check_operand=IO_READ_ADDRESS, check_operand_type=[OperandType.ADDRESS]
    ),
    MicroCode(latch_dr=True),
    BranchingMicroCode("execute2"),
    MicroCode(data_io_mux_sel=DataIoMuxSel.SEL_IO, latch_dr=True, alias="fetch_from_io"),
    BranchingMicroCode("add", check_op_code=[OpCode.ADD], alias="execute2"),
    BranchingMicroCode("sub", check_op_code=[OpCode.SUB]),
    BranchingMicroCode("and", check_op_code=[OpCode.AND]),
    BranchingMicroCode("or", check_op_code=[OpCode.OR]),
    BranchingMicroCode("shl", check_op_code=[OpCode.SHL]),
    BranchingMicroCode("shr", check_op_code=[OpCode.SHR]),
    BranchingMicroCode("cmp", check_op_code=[OpCode.CMP]),
    MicroCode(alu_rop_sel=AluRopSel.SEL_DR, latch_ac=True, alias="ld"),
    BranchingMicroCode("end"),
    BranchingMicroCode(
        "st_to_io",
        check_operand=IO_WRITE_ADDRESS,
        check_operand_type=[OperandType.ADDRESS],
        alias="st",
    ),
    MicroCode(alu_lop_sel=AluLopSel.SEL_AC, latch_data=True),
    BranchingMicroCode("end"),
    MicroCode(alu_lop_sel=AluLopSel.SEL_AC, latch_io=True, alias="st_to_io"),
    BranchingMicroCode("end"),
    MicroCode(
        alu_lop_sel=AluLopSel.SEL_AC,
        alu_rop_sel=AluRopSel.SEL_DR,
        alu_op=AluOp.ADD,
        latch_br=True,
        latch_ps=True,
        alias="add",
    ),
    BranchingMicroCode("math_end"),
    MicroCode(
        alu_lop_sel=AluLopSel.SEL_AC,
        alu_rop_sel=AluRopSel.SEL_DR,
        alu_op=AluOp.SUB,
        latch_br=True,
        latch_ps=True,
        alias="sub",
    ),
    BranchingMicroCode("math_end"),
    MicroCode(
        alu_lop_sel=AluLopSel.SEL_AC,
        alu_rop_sel=AluRopSel.SEL_DR,
        alu_op=AluOp.AND,
        latch_br=True,
        latch_ps=True,
        alias="and",
    ),
    BranchingMicroCode("math_end"),
    MicroCode(
        alu_lop_sel=AluLopSel.SEL_AC,
        alu_rop_sel=AluRopSel.SEL_DR,
        alu_op=AluOp.OR,
        latch_br=True,
        latch_ps=True,
        alias="or",
    ),
    BranchingMicroCode("math_end"),
    MicroCode(
        alu_lop_sel=AluLopSel.SEL_AC,
        alu_rop_sel=AluRopSel.SEL_DR,
        alu_op=AluOp.SHL,
        latch_br=True,
        latch_ps=True,
        alias="shl",
    ),
    BranchingMicroCode("math_end"),
    MicroCode(
        alu_lop_sel=AluLopSel.SEL_AC,
        alu_rop_sel=AluRopSel.SEL_DR,
        alu_op=AluOp.SHR,
        latch_br=True,
        latch_ps=True,
        alias="shr",
    ),
    MicroCode(alu_lop_sel=AluLopSel.SEL_BR, latch_ac=True, alias="math_end"),
    BranchingMicroCode("end"),
    MicroCode(alu_rop_sel=AluRopSel.SEL_SP, alu_op=AluOp.DEC, latch_br=True, alias="push"),
    MicroCode(alu_lop_sel=AluLopSel.SEL_BR, latch_sp=True, latch_ar=True),
    MicroCode(alu_lop_sel=AluLopSel.SEL_AC, latch_data=True),
    BranchingMicroCode("end"),
    MicroCode(alu_rop_sel=AluRopSel.SEL_SP, latch_br=True, alias="pop"),
    MicroCode(alu_lop_sel=AluLopSel.SEL_BR, alu_op=AluOp.INC, latch_sp=True),
    BranchingMicroCode("end"),
    MicroCode(latch_hlt=True, alias="hlt"),
    BranchingMicroCode("end"),
    MicroCode(
        alu_lop_sel=AluLopSel.SEL_AC,
        alu_rop_sel=AluRopSel.SEL_DR,
        alu_op=AluOp.SUB,
        latch_ps=True,
        alias="cmp",
    ),
    BranchingMicroCode("end"),
    BranchingMicroCode("jnz", check_op_code=[OpCode.JNZ], alias="jump_routing"),
    BranchingMicroCode("ja", check_op_code=[OpCode.JA]),
    BranchingMicroCode("jae", check_op_code=[OpCode.JAE]),
    BranchingMicroCode("jbe", check_op_code=[OpCode.JBE]),
    BranchingMicroCode("jb", check_op_code=[OpCode.JB]),
    BranchingMicroCode("jmp", check_op_code=[OpCode.JMP]),
    BranchingMicroCode("jmp", check_z_flag=True, alias="jz"),
    BranchingMicroCode("end"),
    BranchingMicroCode("jmp", check_z_flag=False, alias="jnz"),
    BranchingMicroCode("end"),
    BranchingMicroCode("jmp", check_n_flag=False, alias="jae"),
    BranchingMicroCode("jmp", check_n_flag=False, check_z_flag=False, alias="ja"),
    BranchingMicroCode("end"),
    BranchingMicroCode("end"),
    BranchingMicroCode("jmp", check_n_flag=True, alias="jbe"),
    BranchingMicroCode("jmp", check_n_flag=True, check_z_flag=False, alias="jb"),
    BranchingMicroCode("end"),
    MicroCode(alu_rop_sel=AluRopSel.SEL_DR, latch_pc=True, alias="jmp"),
    BranchingMicroCode("start", alias="end"),
]

commands_alias_to_address_index: dict[str, int] = {}

for index, command in enumerate(runtime):
    if command.alias is not None:
        commands_alias_to_address_index[command.alias] = index

for index, command in enumerate(runtime):
    if isinstance(command, BranchingMicroCode) and isinstance(command.branch_target, str):
        if command.branch_target not in commands_alias_to_address_index:
            raise ValueError(f"Unkonwn alias {command.branch_target} in commnad {index}")
        command.branch_target = commands_alias_to_address_index[command.branch_target]

if __name__ == "__main__":
    for i, code in enumerate(runtime):
        print(i, code)
