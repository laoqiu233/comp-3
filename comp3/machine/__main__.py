import json

from comp3.common.instructions import Program
from comp3.machine.control_unit import ControlUnit
from comp3.machine.datapath import DataPath
from comp3.machine.microcode import runtime

from time import time

if __name__ == "__main__":
    with open("output/examples/euler_problem.json", encoding="utf-8") as file:
        data = json.load(file)
        program = Program(**data)
        input_stream = list(input("IO input: "))
        dp = DataPath(program, input_stream)
        cpu = ControlUnit(dp, runtime)

        start = time()
        cpu.run()
        time_taken = time() - start

        print(f"Program finished executing, ticks taken: {cpu.total_ticks}, time taken: {time_taken}s, tick rate: {round(cpu.total_ticks / time_taken, 2)}Hz")
        print("IO output: ", "".join(map(chr, cpu.datapath.io_interface.output_buffer)))
        print("IO output raw: ", cpu.datapath.io_interface.output_buffer)
