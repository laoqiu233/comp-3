from comp3.compiler.lexer import Lexer
from comp3.compiler.ast import build_nodes_from_tokens
from comp3.compiler.backend import build_program_from_nodes
import json

if __name__ == '__main__':
    with open('examples/hello_user_name.lisq') as file:
        lexer = Lexer(file)
        tokens = lexer.lex()
        nodes = build_nodes_from_tokens(tokens)

        program = build_program_from_nodes(nodes)

        with open('output.json', 'w') as output:
            json.dump(program.model_dump(), output)