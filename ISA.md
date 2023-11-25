# COMP3 Instruction set architecture

## Instruction format

Instructions are stored in JSON, as per the variant given for this task.

The JSON object consists of the following fields:

- op_code
- operand_type
    - immediate
    - address
    - pointer_address
    - stack_offset
    - no_operand
- operand

## Instructions

- Math
    - ADD operand
    - SUB operand
    - AND operand
    - OR operand
    - SHL operand
    - SHR operand

- Memory access
    - LD operand
    - ST operand

- Stack manipulation
    - PUSH
    - POP (The popped element is discarded)

- Branching
    - CMP operand
    - JZ addr
    - JNZ addr
    - JB addr
    - JBE addr
    - JA addr
    - JAE adde
    - JMP addr

## ALU operations

- ADD
- SUB
- AND
- OR
- SHL
- SHR
- +1 (The left operand incremented by one)
- -1 (The right operand decremented by one)
