import re
from enum import Enum
from typing import TextIO

from pydantic import BaseModel


class TokenType(str, Enum):
    IDENTIFIER = "identifier"
    LEFT_PARENTHESIS = "("
    RIGHT_PARENTHESIS = ")"
    INT_LITERAL = "int_literal"
    BOOL_LITERAL = "bool_literal"
    STRING_LITERAL = "string_literal"


class Token(BaseModel):
    token_type: TokenType
    value: str
    line: int
    pos: int


class Lexer:
    def __init__(self, io: TextIO):
        self.line = 1
        self.pos = 1
        self.io = io

    def _consume_spaces(self) -> str:
        char: str

        while re.match(r"\s", char := self.io.read(1)):
            if char == "\n":
                self.line += 1
                self.pos = 1
            else:
                self.pos += 1

        return char

    def build_left_parenthesis(self):
        token = Token(
            token_type=TokenType.LEFT_PARENTHESIS,
            value="(",
            line=self.line,
            pos=self.pos,
        )
        self.pos += 1
        return token

    def build_right_parenthesis(self):
        token = Token(
            token_type=TokenType.RIGHT_PARENTHESIS,
            value=")",
            line=self.line,
            pos=self.pos,
        )
        self.pos += 1
        return token

    def build_string_literal(self):
        string_literal = ""
        while (char := self.io.read(1)) != '"':
            if char == "\n":
                raise ValueError(f"Unexpected line break at line {self.line} col {self.pos}")
            self.pos += 1
            string_literal += char

        return Token(
            token_type=TokenType.STRING_LITERAL,
            value=string_literal,
            line=self.line,
            pos=self.pos - len(string_literal),
        )

    def build_int_literal(self, first_char: str):
        num = first_char
        while re.match(r"[0-9]", (char := self.io.read(1))) is not None:
            num += char
        self.io.seek(self.io.tell() - 1)
        if re.match(r"[\s\(\)]", char) is None:
            raise ValueError(
                f"Unexpected character '{char}' at line {self.line} col {self.pos+len(num)}"
            )
        self.pos += len(num)
        return Token(
            token_type=TokenType.INT_LITERAL,
            value=num,
            line=self.line,
            pos=self.pos,
        )

    def build_identifier(self, first_char: str):
        identifier = first_char
        while re.match(r"[\s\(\)]", (char := self.io.read(1))) is None:
            identifier += char
        self.io.seek(self.io.tell() - 1)
        self.pos += len(identifier)
        if identifier in ["true", "false"]:
            return Token(
                token_type=TokenType.BOOL_LITERAL,
                value=identifier,
                line=self.line,
                pos=self.pos,
            )
        return Token(
            token_type=TokenType.IDENTIFIER,
            value=identifier,
            line=self.line,
            pos=self.pos,
        )

    def lex(self) -> list[Token]:
        tokens: list[Token] = []
        nest_level: int = 0

        while (char := self._consume_spaces()) != "":
            if char == "(":
                nest_level += 1
                tokens.append(self.build_left_parenthesis())
            elif char == ")":
                tokens.append(self.build_right_parenthesis())
                nest_level -= 1
                if nest_level < 0:
                    raise ValueError(
                        f"Unexpected closing paranthesis at line {self.line} col {self.pos}"
                    )
                self.pos += 1
            elif char == '"':
                tokens.append(self.build_string_literal())
            elif re.match(r"[0-9]", char) is not None:
                tokens.append(self.build_int_literal(char))
            else:
                tokens.append(self.build_identifier(char))

        if nest_level != 0:
            raise ValueError("Unexpected EOF")
        return tokens


if __name__ == "__main__":
    with open("examples/cat.lisq", encoding="utf-8") as file:
        lexer = Lexer(file)
        for parsed_token in lexer.lex():
            print(parsed_token.model_dump_json())
