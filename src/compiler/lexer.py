from typing import TextIO
import re
from enum import Enum
from pydantic import BaseModel

class TokenType(str, Enum):
    IDENTIFIER = 'identifier'
    LEFT_PARENTHESIS = '('
    RIGHT_PARENTHESIS = ')'
    INT_LITERAL = 'int_literal'
    BOOL_LITERAL = 'bool_literal'
    STRING_LITERAL = 'string_literal'

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

        while re.match(r'\s', char := self.io.read(1)):
            if char == '\n':
                self.line += 1
                self.pos = 1
            else:
                self.pos += 1

        return char

    def lex(self) -> list[Token]:
        tokens: list[Token] = []
        nest_level: int = 0

        while (char := self._consume_spaces()) != '':
            if char == '(':
                tokens.append(Token(
                    token_type=TokenType.LEFT_PARENTHESIS,
                    value = char,
                    line = self.line,
                    pos = self.pos
                ))
                self.pos += 1
                nest_level += 1
            elif char == ')':
                tokens.append(Token(
                    token_type=TokenType.RIGHT_PARENTHESIS,
                    value = char,
                    line = self.line,
                    pos = self.pos
                ))
                nest_level -= 1
                if nest_level < 0:
                    raise ValueError(f"Unexpected closing paranthesis at line {self.line} col {self.pos}")
                self.pos += 1
            elif char == '"':
                string_literal = ''
                while (char := self.io.read(1)) != '"':
                    if char == '\n':
                        raise ValueError(f"Unexpected line break at line {self.line} col {self.pos}")
                    self.pos += 1
                    string_literal += char
                    
                tokens.append(Token(
                    token_type=TokenType.STRING_LITERAL,
                    value=string_literal,
                    line=self.line,
                    pos=self.pos - len(string_literal)
                ))
            elif re.match(r'[0-9]', char) is not None:
                num = char
                while re.match(r'[0-9]', (char := self.io.read(1))) is not None:
                    num += char
                self.io.seek(self.io.tell() - 1)
                if re.match(r'\s', char) is None:
                    raise ValueError(f"Unexpected character '{char}' at line {self.line} col {self.pos+len(num)}")
                tokens.append(Token(
                    token_type=TokenType.INT_LITERAL,
                    value=num,
                    line=self.line,
                    pos=self.pos
                ))
                self.pos += len(num)
            else:
                identifier = char
                while re.match(r'[\s\(\)]', (char := self.io.read(1))) is None:
                    identifier += char
                self.io.seek(self.io.tell() - 1)

                if (identifier == 'true' or identifier == 'false'):
                    tokens.append(Token(
                        token_type=TokenType.BOOL_LITERAL,
                        value=identifier,
                        line=self.line,
                        pos=self.pos
                    ))
                else:
                    tokens.append(Token(
                        token_type=TokenType.IDENTIFIER,
                        value=identifier,
                        line=self.line,
                        pos=self.pos
                    ))
                self.pos += len(identifier)

        return tokens