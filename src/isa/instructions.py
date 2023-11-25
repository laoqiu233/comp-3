from enum import Enum
from pydantic import BaseModel, Field

class OpCode(str, Enum):
    # Math operations
    ADD = 'ADD'
    SUB = 'SUB'
    AND = 'AND'
    OR = 'OR'
    SHL = 'SHL'
    SHR = 'SHR'

    # Memory access
    LD = 'LD'
    ST = 'ST'

    # Stack manipulation
    PUSH = 'PUSH'
    POP = 'POP'

    # Branching
    CMP = 'CMP'
    JZ = 'JZ'
    JNZ = 'JNZ'
    JLT = 'JLT'
    JGT = 'JGT'
    JMP = 'JMP'
    
class OperandType(str, Enum):
    IMMEDIATE = 'immediate'
    ADDRESS = 'address'
    POINTER_ADDRESS = 'pointer_address'
    STACK_OFFSET = 'stack_offset'

class AluOp(Enum):
    ADD = 0
    SUB = 1
    AND = 2
    OR = 3
    SHL = 4
    SHR = 5
    INC = 6 # Increase left operand
    DEC = 7 # Decrease right operand

class Instruction(BaseModel):
    op_code: OpCode
    operand_type: OperandType
    operand: int = Field(ge=0, lt=2**32)