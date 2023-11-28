from comp3.machine.datapath import DataPath
from comp3.machine.microcode import BranchingMicroCode, MicroCode


class ControlUnit:
    def __init__(self, datapath: DataPath, runtime: list[MicroCode | BranchingMicroCode]):
        self.runtime = runtime
        self.datapath = datapath
        self.mpc = 0
        self.total_ticks = 0

    def execute_microcode(self):
        print(f"Microcode {self.mpc}: {self.runtime[self.mpc]}")
        microcode = self.runtime[self.mpc]
        self.mpc += 1

        if isinstance(microcode, MicroCode):
            microcode.execute(self.datapath)
        else:
            if microcode.execute(self.datapath):
                if isinstance(microcode.branch_target, str):
                    raise ValueError(
                        "Microcode branch target not converted to int"
                    )  # This should not happen, I hope
                self.mpc = microcode.branch_target

        print(self.datapath)
        self.total_ticks += 1

    def run(self):
        while not self.datapath.ps.hlt:
            self.execute_microcode()
            # input("...")
