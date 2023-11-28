from enum import Enum


class AluLopSel(Enum):
    SEL_AC = 0
    SEL_BR = 1
    SEL_IR = 2
    SEL_ZERO = 3


class AluRopSel(Enum):
    SEL_DR = 0
    SEL_AR = 1
    SEL_SP = 2
    SEL_ZERO = 3


class BrMuxSel(Enum):
    SEL_ALU = 0
    SEL_PC = 1


class DataIoMuxSel(Enum):
    SEL_DATA = 0
    SEL_IO = 1


class DrMuxSel(Enum):
    SEL_ALU = 0
    SEL_DATA = 1


IO_READ_ADDRESS = 42
IO_WRITE_ADDRESS = 69
