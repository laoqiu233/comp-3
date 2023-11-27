from dataclasses import dataclass
from typing import Optional

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

    alu_lop_sel: AluLopSel
    alu_rop_sel: AluRopSel
    data_io_mux_sel: DataIoMuxSel
    br_mux_sel: BrMuxSel
    dr_mux_sel: DrMuxSel
    alu_op: AluOp

    latch_ac: bool
    latch_br: bool
    latch_ir: bool
    latch_dr: bool
    latch_ar: bool
    latch_sp: bool
    latch_pc: bool
    latch_io: bool
    latch_data: bool

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

    def __str__(self) -> str:
        s = ""

        if self.latch_ac:
            s += f"AC <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_br:
            s += f"AC <- {self.br_mux_sel} "

        if self.latch_ir:
            s += "IR <- INSTR_MEMORY "

        if self.latch_dr:
            if self.dr_mux_sel == DrMuxSel.SEL_ALU:
                s += f"DR <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "
            elif self.dr_mux_sel == DrMuxSel.SEL_DATA:
                s += f"DR <- {self.data_io_mux_sel} "

        if self.latch_ar:
            s += f"AR <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_sp:
            s += f"SP <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_io:
            s += f"IO <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_data:
            s += f"DATA <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.alias is not None:
            s += f" ({self.alias})"

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

    check_op_code: Optional[OpCode]
    check_operand: Optional[OperandType]
    check_c_flag: Optional[bool]
    check_n_flag: Optional[bool]
    check_z_flag: Optional[bool]

    alias: Optional[str] = None

    def execute(self, datapath: DataPath) -> bool:
        if (
            self.check_op_code is not None
            and datapath.ir.get_instruction().op_code != self.check_op_code
        ):
            return False

        if (
            self.check_operand is not None
            and datapath.ir.get_instruction().operand_type != self.check_operand
        ):
            return False

        if self.check_c_flag is not None and datapath.alu.c_flag != self.check_c_flag:
            return False

        if self.check_n_flag is not None and datapath.alu.n_flag != self.check_n_flag:
            return False

        if self.check_z_flag is not None and datapath.alu.z_flag != self.check_z_flag:
            return False

        return True

    def __str__(self) -> str:
        s = f"JUMP TO {self.branch_target} IF "

        if self.check_op_code is not None:
            s += f"OP_CODE = {self.check_op_code} "

        if self.check_operand is not None:
            s += f"OPERNAD = {self.check_operand} "

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
    # Fetch instruction
    MicroCode(
        AluLopSel.SEL_ZERO,
        AluRopSel.SEL_ZERO,
        DataIoMuxSel.SEL_DATA,
        BrMuxSel.SEL_ALU,
        DrMuxSel.SEL_DATA,
        AluOp.ADD,
        latch_ac=False,
        latch_br=False,
        latch_ir=True,
        latch_dr=False,
        latch_ar=False,
        latch_sp=False,
        latch_pc=False,
        latch_io=False,
        latch_data=False,
    ),
    BranchingMicroCode(
        branch_target="fetch_immediate",
        check_op_code=None,
        check_operand=OperandType.IMMEDIATE,
        check_c_flag=None,
        check_n_flag=None,
        check_z_flag=None,
    ),
    BranchingMicroCode(
        branch_target="fetch_address",
        check_op_code=None,
        check_operand=OperandType.ADDRESS,
        check_c_flag=None,
        check_n_flag=None,
        check_z_flag=None,
    ),
    BranchingMicroCode(
        branch_target="fetch_pointer_address",
        check_op_code=None,
        check_operand=OperandType.POINTER_ADDRESS,
        check_c_flag=None,
        check_n_flag=None,
        check_z_flag=None,
    ),
    # Stack offset
    MicroCode(
        AluLopSel.SEL_IR,
        AluRopSel.SEL_ZERO,
        DataIoMuxSel.SEL_DATA,
        BrMuxSel.SEL_ALU,
        DrMuxSel.SEL_ALU,
        AluOp.ADD,
        latch_ac=False,
        latch_br=False,
        latch_ir=False,
        latch_dr=True,
        latch_ar=False,
        latch_sp=False,
        latch_pc=False,
        latch_io=False,
        latch_data=False,
        alias="fetch_immediate",
    ),
    MicroCode(
        AluLopSel.SEL_IR,
        AluRopSel.SEL_ZERO,
        DataIoMuxSel.SEL_DATA,
        BrMuxSel.SEL_ALU,
        DrMuxSel.SEL_ALU,
        AluOp.ADD,
        latch_ac=False,
        latch_br=False,
        latch_ir=False,
        latch_dr=False,
        latch_ar=True,
        latch_sp=False,
        latch_pc=False,
        latch_io=False,
        latch_data=False,
        alias="fetch_address",
    ),
    MicroCode(
        AluLopSel.SEL_ZERO,
        AluRopSel.SEL_ZERO,
        DataIoMuxSel.SEL_DATA,
        BrMuxSel.SEL_ALU,
        DrMuxSel.SEL_DATA,
        AluOp.ADD,
        latch_ac=False,
        latch_br=False,
        latch_ir=False,
        latch_dr=True,
        latch_ar=False,
        latch_sp=False,
        latch_pc=False,
        latch_io=False,
        latch_data=False,
    ),
    MicroCode(
        AluLopSel.SEL_IR,
        AluRopSel.SEL_ZERO,
        DataIoMuxSel.SEL_DATA,
        BrMuxSel.SEL_ALU,
        DrMuxSel.SEL_DATA,
        AluOp.ADD,
        latch_ac=False,
        latch_br=False,
        latch_ir=False,
        latch_dr=False,
        latch_ar=True,
        latch_sp=False,
        latch_pc=False,
        latch_io=False,
        latch_data=False,
        alias="fetch_pointer_address",
    ),
    MicroCode(
        AluLopSel.SEL_ZERO,
        AluRopSel.SEL_ZERO,
        DataIoMuxSel.SEL_DATA,
        BrMuxSel.SEL_ALU,
        DrMuxSel.SEL_DATA,
        AluOp.ADD,
        latch_ac=False,
        latch_br=False,
        latch_ir=False,
        latch_dr=True,
        latch_ar=False,
        latch_sp=False,
        latch_pc=False,
        latch_io=False,
        latch_data=False,
    ),
    MicroCode(
        AluLopSel.SEL_ZERO,
        AluRopSel.SEL_DR,
        DataIoMuxSel.SEL_DATA,
        BrMuxSel.SEL_ALU,
        DrMuxSel.SEL_DATA,
        AluOp.ADD,
        latch_ac=False,
        latch_br=False,
        latch_ir=False,
        latch_dr=False,
        latch_ar=True,
        latch_sp=False,
        latch_pc=False,
        latch_io=False,
        latch_data=False,
    ),
    MicroCode(
        AluLopSel.SEL_ZERO,
        AluRopSel.SEL_ZERO,
        DataIoMuxSel.SEL_DATA,
        BrMuxSel.SEL_ALU,
        DrMuxSel.SEL_DATA,
        AluOp.ADD,
        latch_ac=False,
        latch_br=False,
        latch_ir=False,
        latch_dr=True,
        latch_ar=False,
        latch_sp=False,
        latch_pc=False,
        latch_io=False,
        latch_data=False,
    ),
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
