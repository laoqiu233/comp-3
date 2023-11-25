from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

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
    JA = 'JA'
    JAE = 'JAE'
    JB = 'JB'
    JBE = 'JBE'
    JMP = 'JMP'
    
class OperandType(str, Enum):
    IMMEDIATE = 'immediate'
    ADDRESS = 'address'
    POINTER_ADDRESS = 'pointer_address'
    STACK_OFFSET = 'stack_offset'
    NO_OPERAND = 'no_operand'

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

    # Should not be serialized in JSON
    # Used for stubbing
    instr_id: Optional[int] = Field(exclude=True, default=None)

class DataStubInstruction(Instruction):
    data_stub_identifier: str
    
class InstrStubInstruction(Instruction):
    referenced_instr_id: int
    referenced_instr_offset: int

class Program(BaseModel):
    instructions: list[Instruction]