import logging

from comp3.common.instructions import OpCode
from comp3.machine.datapath import DataPath
from comp3.machine.microcode import BranchingMicroCode, MicroCode


logger = logging.getLogger("machine.control_unit")


class ControlUnit:
    def __init__(self, datapath: DataPath, runtime: list[MicroCode | BranchingMicroCode]):
        self.runtime = runtime
        self.datapath = datapath
        self.mpc = 0
        self.total_ticks = 0
        self.total_instructions = 0

        self._op_code_to_address: dict[OpCode, int] = {}

        for index, instr in enumerate(runtime):
            if instr.alias is not None and isinstance(instr.alias, OpCode):
                self._op_code_to_address[instr.alias] = index

    def execute_microcode(self):
        logger.debug("Microcode %s: %s", self.mpc, self.runtime[self.mpc])
        microcode = self.runtime[self.mpc]
        # Instruction fetch
        if self.mpc == 0:
            self.total_instructions += 1
        self.mpc += 1

        if isinstance(microcode, MicroCode):
            microcode.execute(self.datapath)
        else:
            if microcode.execute(self.datapath):
                if isinstance(microcode.branch_target, str):
                    raise ValueError(
                        "Microcode branch target not converted to int"
                    )  # This should not happen, I hope

                if microcode.branch_target is None:
                    self.mpc = self._op_code_to_address[self.datapath.ir.value.op_code]
                else:
                    self.mpc = microcode.branch_target

        logger.debug(self.datapath)
        self.total_ticks += 1

    def run(self):
        while not self.datapath.ps.hlt:
            self.execute_microcode()
