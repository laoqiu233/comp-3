from comp3.common.instructions import AluOp, Program
from comp3.machine.common import AluLopSel, AluRopSel, BrMuxSel, DataIoMuxSel, DrMuxSel
from comp3.machine.components import (
    ALU,
    DataMemory,
    InstructionMemory,
    InstructionRegister,
    IoInterface,
    Mux,
    ProgramStatus,
    Register,
    ZeroReg,
)


# pylint: disable=too-many-instance-attributes
class DataPath:
    def __init__(self, program: Program, input_stream: list[str]):
        # Wiring
        self.zero_reg = ZeroReg()

        self.alu_left_operand_mux = Mux()  # Create now, add later
        self.alu_right_operand_mux = Mux()  # Create now, add later
        self.alu = ALU(self.alu_left_operand_mux, self.alu_right_operand_mux)

        self.ac = Register(self.alu)
        self.ar = Register(self.alu)
        self.sp = Register(self.alu)
        self.sp.val = 4096  # Initialized to point to 1 above 4kb
        self.pc = Register(self.alu)

        self.instruction_memory = InstructionMemory(self.pc, program.instructions)
        self.ir = InstructionRegister(self.instruction_memory)

        self.data_memory = DataMemory(self.alu, self.ar, program.data_memory)
        self.io_interface = IoInterface(self.alu, input_stream)

        self.data_io_mux = Mux(self.data_memory, self.io_interface)
        self.dr_mux = Mux(self.alu, self.data_io_mux)
        self.dr = Register(self.dr_mux)

        self.br_mux = Mux(self.alu, self.pc)
        self.br = Register(self.br_mux)

        self.alu_left_operand_mux.input_regs = (self.ac, self.br, self.ir, self.zero_reg)
        self.alu_right_operand_mux.input_regs = (self.dr, self.ar, self.sp, self.zero_reg)

        self.ps = ProgramStatus(self.alu)

    def __str__(self) -> str:
        return (
            f"AC: {self.ac.val} | AR: {self.ar.val} | SP: {self.sp.val} | PC: {self.pc.val} | IR:"
            f" {self.ir.value.model_dump_json()} | DR: {self.dr.val} | BR: {self.br.val} | N:"
            f" {self.ps.n} | Z: {self.ps.z} | C: {self.ps.c}"
        )

    # Signals
    def latch_ac(self):
        self.ac.latch()

    def latch_br(self):
        self.br.latch()

    def latch_ir(self):
        self.ir.latch()

    def latch_pc(self):
        self.pc.latch()

    def latch_dr(self):
        self.dr.latch()

    def latch_ar(self):
        self.ar.latch()

    def latch_sp(self):
        self.sp.latch()

    def write_io(self):
        self.io_interface.latch()

    def write_data(self):
        self.data_memory.latch()

    def latch_ps(self):
        self.ps.latch()

    def clear_ps(self):
        self.ps.clear()

    def latch_hlt(self):
        self.ps.latch_hlt()

    # Mux selections
    def sel_br_mux(self, sel: BrMuxSel):
        self.br_mux.select(sel.value)

    def sel_alu_lop(self, sel: AluLopSel):
        self.alu_left_operand_mux.select(sel.value)

    def sel_alu_rop(self, sel: AluRopSel):
        self.alu_right_operand_mux.select(sel.value)

    def sel_dr_mux(self, sel: DrMuxSel):
        self.dr_mux.select(sel.value)

    def sel_data_io_mux(self, sel: DataIoMuxSel):
        self.data_io_mux.select(sel.value)

    def sel_alu_op(self, sel: AluOp):
        self.alu.select_op(sel)
