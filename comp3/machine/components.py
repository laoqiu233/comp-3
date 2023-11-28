from abc import ABC, abstractmethod

from comp3.common.instructions import AluOp, DataWord, Instruction


# pylint: disable=too-few-public-methods
class ValueStore(ABC):
    @abstractmethod
    def get_value(self) -> int:
        pass


# pylint: disable=too-few-public-methods
class ZeroReg(ValueStore):
    def get_value(self) -> int:
        return 0


class Register(ValueStore):
    def __init__(self, input_reg: ValueStore):
        self.input_reg = input_reg
        self.val = 0

    def latch(self):
        self.val = self.input_reg.get_value()

    def get_value(self) -> int:
        return self.val


class Mux(ValueStore):
    def __init__(self, *input_regs: ValueStore):
        self.input_regs = input_regs
        self.selected = 0

    def select(self, selected: int):
        self.selected = selected

    def get_value(self) -> int:
        return self.input_regs[self.selected].get_value()


# pylint: disable=too-few-public-methods
class InstructionMemory:
    def __init__(self, pc: ValueStore, instructions: list[Instruction]):
        self.pc = pc
        self.instructions = instructions

    def get_instruction(self) -> Instruction:
        index = self.pc.get_value()
        return self.instructions[index]


class InstructionRegister(ValueStore):
    def __init__(self, memory: InstructionMemory):
        self.memory = memory
        self.value = memory.get_instruction()

    def latch(self):
        self.value = self.memory.get_instruction()

    def get_value(self) -> int:
        return self.value.operand

    def get_instruction(self) -> Instruction:
        return self.value


class IoIntercae(ValueStore):
    def __init__(self, input_reg: ValueStore, char_stream: list[str]):
        self.input_reg = input_reg
        self.char_stream = char_stream
        self.char_pointer = 0
        self.output_buffer: list[int] = []

    def get_value(self) -> int:
        if self.char_pointer >= len(self.char_stream):
            return 0
        self.char_pointer += 1
        return ord(self.char_stream[self.char_pointer - 1])

    def latch(self):
        self.output_buffer.append(self.input_reg.get_value() % 2**8)


class DataMemory(ValueStore):
    def __init__(self, data_in: ValueStore, address_in: ValueStore, memory: list[DataWord]):
        self.data_in = data_in
        self.address_in = address_in
        self.memory: dict[int, int] = {}

        for index, word in enumerate(memory):
            self.memory[index] = word.value

    def latch(self):
        address = self.address_in.get_value()
        data = self.data_in.get_value()
        self.memory[address] = data

    def get_value(self) -> int:
        address = self.address_in.get_value()
        return self.memory.get(address, 0)


class ALU(ValueStore):
    def __init__(self, left_operand: ValueStore, right_operand: ValueStore):
        self.left_operand = left_operand
        self.right_operand = right_operand
        self.alu_op = AluOp.ADD
        self.n_flag = False
        self.z_flag = False
        self.c_flag = False

    @classmethod
    def get_compliment(cls, value: int) -> int:
        value ^= (1 << 32) - 1
        return (value + 1) % (1 << 32)

    @classmethod
    def is_neg(cls, value: int) -> bool:
        return value & (1 << 31) != 0

    def add(self, left: int, right: int) -> int:
        res = left + right

        self.c_flag = res >= (1 << 32)
        res %= 1 << 32
        self.z_flag = res == 0
        self.n_flag = ALU.is_neg(res)

        return res

    def select_op(self, alu_op: AluOp):
        self.alu_op = alu_op

    def check_bit_operations(self, left: int, right: int) -> int:
        self.c_flag = False
        self.n_flag = False
        self.z_flag = False
        if self.alu_op == AluOp.OR:
            return left | right
        if self.alu_op == AluOp.AND:
            return left & right
        if self.alu_op == AluOp.SHR:
            res = left >> right
            if res == 0:
                self.z_flag = True
            return res
        if self.alu_op == AluOp.SHL:
            res = left << right
            if res >= (1 << 32):
                self.c_flag = True
            res %= 1 << 32
            if ALU.is_neg(res):
                self.n_flag = True
            if res == 0:
                self.z_flag = True
            return res
        if self.alu_op == AluOp.NOT:
            res = left ^ ((1 << 32) - 1)
            if ALU.is_neg(res):
                self.n_flag = True
            if res == 0:
                self.z_flag = True
            return res

        raise ValueError("DEBUG: Inavlid alu op? This should not happen")

    def get_value(self) -> int:
        left = self.left_operand.get_value()
        right = self.right_operand.get_value()

        if self.alu_op == AluOp.ADD:
            return self.add(left, right)
        if self.alu_op == AluOp.SUB:
            right = ALU.get_compliment(right)
            return self.add(left, right)
        if self.alu_op == AluOp.INC:
            return self.add(left, 1)
        if self.alu_op == AluOp.DEC:
            return self.add(right, (1 << 32) - 1)

        return self.check_bit_operations(left, right)


class ProgramStatus:
    def __init__(self, alu: ALU):
        self.alu = alu
        self.n = alu.n_flag
        self.z = alu.z_flag
        self.c = alu.c_flag
        self.hlt = False

    def latch(self):
        self.alu.get_value()
        self.n = self.alu.n_flag
        self.z = self.alu.z_flag
        self.c = self.alu.c_flag

    def latch_hlt(self):
        self.hlt = True

    def clear(self):
        self.n = False
        self.z = False
        self.c = False
