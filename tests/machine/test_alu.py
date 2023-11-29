import pytest

from comp3.common.instructions import AluOp
from comp3.machine.components import ALU, ValueStore


# pylint: disable=too-few-public-methods
class StubRegister(ValueStore):
    def __init__(self):
        self.val = 0

    def get_value(self) -> int:
        return self.val


@pytest.mark.parametrize(
    ("val", "expected"), ((0, 0), (1, (1 << 32) - 1), (52, 0b11111111111111111111111111001100))
)
def test_compliment(val: int, expected: int):
    assert ALU.get_compliment(val) == expected


def test_alu_addition():
    left = StubRegister()
    right = StubRegister()

    alu = ALU(left, right)

    alu.select_op(AluOp.ADD)

    left.val = 1
    right.val = 1
    res = alu.get_value()

    assert res == 2
    assert not alu.c_flag
    assert not alu.n_flag
    assert not alu.z_flag


def test_alu_add_zero():
    left = StubRegister()
    right = StubRegister()

    alu = ALU(left, right)

    alu.select_op(AluOp.ADD)

    left.val = 52
    right.val = 0
    res = alu.get_value()

    assert res == 52
    assert not alu.c_flag
    assert not alu.n_flag
    assert not alu.z_flag


def test_alu_overflow_add():
    left = StubRegister()
    right = StubRegister()

    alu = ALU(left, right)

    alu.select_op(AluOp.ADD)

    left.val = (1 << 31) - 1
    right.val = 1
    res = alu.get_value()

    assert res == 1 << 31
    assert not alu.c_flag
    assert alu.n_flag
    assert not alu.z_flag


def test_alu_above_or_equals():
    left = StubRegister()
    right = StubRegister()

    alu = ALU(left, right)

    alu.select_op(AluOp.SUB)

    left.val = 52
    right.val = 52
    alu.get_value()

    assert not alu.n_flag or alu.z_flag


def test_alu_below():
    left = StubRegister()
    right = StubRegister()

    alu = ALU(left, right)

    alu.select_op(AluOp.SUB)

    left.val = 0
    right.val = 52
    alu.get_value()

    assert alu.n_flag
