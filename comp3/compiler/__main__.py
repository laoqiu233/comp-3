from comp3.compiler.lexer import Lexer
from comp3.compiler.ast import build_nodes_from_tokens
from comp3.compiler.backend import Comp3Backend, replace_stubs
from comp3.common.instructions import Instruction, Program
import json

if __name__ == '__main__':
    with open('examples/cat.lisq') as file:
        lexer = Lexer(file)
        tokens = lexer.lex()
        nodes = build_nodes_from_tokens(tokens)

        whole_program: list[Instruction] = []

        for node in nodes:
            backend = Comp3Backend()
            backend.visit(node)
            whole_program += backend.program

        with open('output.json', 'w') as file:
            program = Program(instructions=whole_program)
            replace_stubs(program)
            json.dump(program.model_dump(), file)
                