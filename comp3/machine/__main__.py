import json

from comp3.common.instructions import Program
from comp3.machine.control_unit import ControlUnit
from comp3.machine.datapath import DataPath
from comp3.machine.microcode import runtime


if __name__ == "__main__":
    with open("output.json", encoding="utf-8") as file:
        data = json.load(file)
        program = Program(**data)
        input_stream = list(input("Program IO input: "))
        dp = DataPath(program, input_stream)
        cpu = ControlUnit(dp, runtime)
        cpu.run()