import json
from io import StringIO
from typing import TextIO

from comp3.compiler.ast import build_nodes_from_tokens
from comp3.compiler.backend import build_program_from_nodes
from comp3.compiler.lexer import Lexer
from comp3.compiler.preprocessing import process_includes


def compile_pipeline(source: TextIO, output: TextIO):
    content = source.read()
    content = process_includes(content)
    lexer = Lexer(StringIO(content))
    tokens = lexer.lex()
    nodes = build_nodes_from_tokens(tokens)
    program = build_program_from_nodes(nodes)
    json.dump(program.model_dump(), output)


__all__ = ["compile_pipeline"]
