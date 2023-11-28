from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from comp3.compiler.lexer import Token, TokenType


class AstBackend(ABC):
    @abstractmethod
    def visit(self, node: "AstNode"):
        pass

    @abstractmethod
    def visit_let_var_node(self, node: "LetVarNode"):
        pass

    @abstractmethod
    def visit_let_node(self, node: "LetNode"):
        pass

    @abstractmethod
    def visit_set_node(self, node: "SetNode"):
        pass

    @abstractmethod
    def visit_set_ptr_node(self, node: "SetPtrNode"):
        pass

    @abstractmethod
    def visit_loop_while_node(self, node: "LoopWhileNode"):
        pass

    @abstractmethod
    def visit_math_node(self, node: "MathNode"):
        pass

    @abstractmethod
    def visit_get_char_node(self, node: "GetCharNode"):
        pass

    @abstractmethod
    def visit_put_char_node(self, node: "PutCharNode"):
        pass

    @abstractmethod
    def visit_int_literal_node(self, node: "IntLiteralNode"):
        pass

    @abstractmethod
    def visit_load_by_identifier_node(self, node: "LoadByIdentifierNode"):
        pass

    @abstractmethod
    def visit_load_by_pointer_identifier_node(self, node: "LoadByPointerIdentifierNode"):
        pass

    @abstractmethod
    def visit_func_node(self, node: "FuncNode"):
        pass

    @abstractmethod
    def visit_func_call_node(self, node: "FuncCallNode"):
        pass

    @abstractmethod
    def visit_string_literal_node(self, node: "StringLiteralNode"):
        pass

    @abstractmethod
    def visit_str_alloc_node(self, node: "StrAllocNode"):
        pass

    @abstractmethod
    def visit_if_node(self, node: "IfNode"):
        pass

    @abstractmethod
    def visit_multiple_expressions_node(self, node: "MultipleExpressionNode"):
        pass


# pylint: disable=too-few-public-methods
class AstNode(ABC):
    @abstractmethod
    def compile(self, backend: AstBackend):
        pass


@dataclass
class LetVarNode(AstNode):
    identifier: str
    load_value: AstNode

    def compile(self, backend: AstBackend):
        backend.visit_let_var_node(self)

    def __str__(self) -> str:
        return f"""{self.identifier} = {self.load_value}"""


@dataclass
class LetNode(AstNode):
    start_token: Token
    end_token: Token
    var_nodes: list[LetVarNode]
    body: list[AstNode]

    def append_node(self, node: AstNode):
        self.body.append(node)

    def compile(self, backend: AstBackend):
        backend.visit_let_node(self)

    def __str__(self) -> str:
        s = f"""(
\tlet ({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tvars:\n"""
        for var in self.var_nodes:
            s += "\t\t" + "\t\t".join(str(var).splitlines(True)) + "\n"
        s += "\tbody:\n"
        for expr in self.body:
            s += "\t\t" + "\t\t".join(str(expr).splitlines(True)) + "\n"
        s += "\n)"

        return s


@dataclass
class SetNode(AstNode):
    start_token: Token
    end_token: Token
    identifier: str
    load_value: AstNode

    def compile(self, backend: AstBackend):
        backend.visit_set_node(self)

    def __str__(self) -> str:
        return f"""(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tset
\t{self.identifier}
\tto\n\t""" + "\t".join(str(self.load_value).splitlines(True)) + "\n)"


@dataclass
class SetPtrNode(AstNode):
    start_token: Token
    end_token: Token
    identifier: str
    load_value: AstNode

    def compile(self, backend: AstBackend):
        backend.visit_set_ptr_node(self)


@dataclass
class LoopWhileNode(AstNode):
    start_token: Token
    end_token: Token
    loop_condition: AstNode
    body: list[AstNode]

    def compile(self, backend: AstBackend):
        backend.visit_loop_while_node(self)

    def __str__(self) -> str:
        s = f"""(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tloop while\n"""
        s += "\t\t" + "\t\t".join(str(self.loop_condition).splitlines(True)) + "\n\tdo\n"

        for expr in self.body:
            s += "\t\t" + "\t\t".join(str(expr).splitlines(True)) + "\n"
        s += ")"
        return s


@dataclass
class GetCharNode(AstNode):
    start_token: Token
    end_token: Token

    def compile(self, backend: AstBackend):
        backend.visit_get_char_node(self)

    def __str__(self) -> str:
        return (
            f"get_char ({self.start_token.line}-{self.start_token.pos} to"
            f" {self.end_token.line}-{self.end_token.pos})"
        )


@dataclass
class PutCharNode(AstNode):
    start_token: Token
    end_token: Token
    load_value: AstNode

    def compile(self, backend: AstBackend):
        backend.visit_put_char_node(self)

    def __str__(self) -> str:
        return f"""(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tput_char\n\t""" + "\t".join(str(self.load_value).splitlines(True)) + "\n)"


@dataclass
class MathNode(AstNode):
    class MathOp(str, Enum):
        ADD = "+"
        SUB = "-"
        AND = "&"
        OR = "|"
        LT = "<"
        LE = "<="
        GT = ">"
        GE = ">="
        EQ = "="
        NE = "!="
        SHL = "<<"
        SHR = ">>"

    start_token: Token
    end_token: Token
    left_operand: AstNode
    right_operand: AstNode
    op: MathOp

    def compile(self, backend: AstBackend):
        backend.visit_math_node(self)

    def __str__(self) -> str:
        s = f"""(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\t"""
        s += "\t".join(str(self.left_operand).splitlines(True))
        s += f"\n\t{self.op.value}\n\t"
        s += "\t".join(str(self.right_operand).splitlines(True))
        s += "\n)"

        return s


@dataclass
class FuncNode(AstNode):
    start_token: Token
    end_token: Token
    identifier: str
    param_identifiers: list[str]
    body: list[AstNode]

    def compile(self, backend: AstBackend):
        backend.visit_func_node(self)

    def __str__(self) -> str:
        s = (
            f'function {self.identifier} ({", ".join(self.param_identifiers)})'
            f" ({self.start_token.line}-{self.start_token.pos} to"
            f" {self.end_token.line}-{self.end_token.pos}) (\n"
        )

        for expr in self.body:
            s += "\t" + "\t".join(str(expr).splitlines(True)) + "\n"

        s += ")"

        return s


@dataclass
class IfNode(AstNode):
    start_token: Token
    end_token: Token
    if_condition: AstNode
    true_expr: AstNode
    false_expr: Optional[AstNode]

    def compile(self, backend: AstBackend):
        backend.visit_if_node(self)

    def __str__(self) -> str:
        s = f"""(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tif\n\t\t"""
        s += "\t\t".join(str(self.if_condition).splitlines(True))
        s += "\n\tthen\n\t\t"
        s += "\t\t".join(str(self.true_expr).splitlines(True))
        if self.false_expr is not None:
            s += "\n\telse\n\t\t"
            s += "\t\t".join(str(self.false_expr).splitlines(True))
        s += "\n)"
        return s


@dataclass
class FuncCallNode(AstNode):
    start_token: Token
    end_token: Token
    func_identifier: str
    params: list[AstNode]

    def compile(self, backend: AstBackend):
        backend.visit_func_call_node(self)

    def __str__(self) -> str:
        s = f"""(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tcall {self.func_identifier}
\t(\n
"""
        for param in self.params:
            s += "\t\t" + "\t\t".join(str(param).splitlines(True)) + "\n"

        s += "\t)\n)"

        return s


@dataclass
class StrAllocNode(AstNode):
    start_token: Token
    end_token: Token
    identifier: str
    size: int

    def compile(self, backend: AstBackend):
        backend.visit_str_alloc_node(self)

    def __str__(self) -> str:
        return f"(alloc_str {self.identifier} {self.size} chars)"


@dataclass
class IntLiteralNode(AstNode):
    token: Token
    value: int

    def compile(self, backend: AstBackend):
        backend.visit_int_literal_node(self)

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class StringLiteralNode(AstNode):
    token: Token
    value: str

    def compile(self, backend: AstBackend):
        backend.visit_string_literal_node(self)

    def __str__(self) -> str:
        return f'"{self.value}"'


@dataclass
class LoadByIdentifierNode(AstNode):
    token: Token
    identifier: str

    def compile(self, backend: AstBackend):
        backend.visit_load_by_identifier_node(self)

    def __str__(self) -> str:
        return f"({self.identifier})"


@dataclass
class LoadByPointerIdentifierNode(AstNode):
    start_token: Token
    end_token: Token
    identifier: str

    def compile(self, backend: AstBackend):
        backend.visit_load_by_pointer_identifier_node(self)

@dataclass
class MultipleExpressionNode(AstNode):
    start_token: Token
    end_token: Token
    expressions: list[AstNode]

    def compile(self, backend: AstBackend):
        backend.visit_multiple_expressions_node(self)


def unexpected_eof(token: Token) -> ValueError:
    return ValueError(
        f"Unexpected EOF reached at line {token.line} col {token.pos + len(token.value)}"
    )


def unexpected_token(token: Token, expected: str) -> ValueError:
    return ValueError(
        f"Unexpected token {token.value} at line {token.line} col {token.pos}, expected {expected}"
    )


class AstBuilder:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.i = 0

    def is_eof(self) -> bool:
        return self.i >= len(self.tokens)

    def _get_next_token(self) -> Token:
        token = self._peek_next_token()
        self.i += 1
        return token

    def _peek_next_token(self) -> Token:
        if self.is_eof():
            raise unexpected_eof(self.tokens[-1])
        return self.tokens[self.i]

    def parse_let_vars(self) -> list[LetVarNode]:
        let_vars: list[LetVarNode] = []
        token = self._get_next_token()

        if token.token_type != TokenType.LEFT_PARENTHESIS:
            raise unexpected_token(token, "(")

        while (token := self._get_next_token()).token_type != TokenType.RIGHT_PARENTHESIS:
            if token.token_type != TokenType.LEFT_PARENTHESIS:
                raise unexpected_token(token, "( for new variable or ) for closing let block")
            identifier_token = self._get_next_token()
            if identifier_token.token_type != TokenType.IDENTIFIER:
                raise unexpected_token(token, "an identifier for the variable")
            load_value = self.parse_node()

            if (closing_token := self._get_next_token()).token_type != TokenType.RIGHT_PARENTHESIS:
                raise unexpected_token(closing_token, ")")

            let_vars.append(LetVarNode(identifier_token.value, load_value))

        return let_vars

    def _try_get_end_token(self) -> Token:
        end_token = self._get_next_token()
        if end_token.token_type != TokenType.RIGHT_PARENTHESIS:
            raise unexpected_token(end_token, ")")
        return end_token

    def parse_loop_node(self, start_token: Token) -> AstNode:
        loop_op = self._get_next_token()

        if loop_op.token_type == TokenType.IDENTIFIER and loop_op.value == "while":
            # (loop while expr do
            #   body_expr
            #   body_expr
            #   ...
            # )
            loop_condition = self.parse_node()
            do_token = self._get_next_token()
            if do_token.token_type != TokenType.IDENTIFIER or do_token.value != "do":
                raise unexpected_token(do_token, "do")
            body: list[AstNode] = []
            while self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
                body.append(self.parse_node())
            end_token = self._get_next_token()
            return LoopWhileNode(start_token, end_token, loop_condition, body)
        raise unexpected_token(loop_op, "while or for")

    def parse_set_node(self, start_token: Token) -> AstNode:
        # (set identifier expr)
        identifier = self._get_next_token()
        if identifier.token_type != TokenType.IDENTIFIER:
            raise unexpected_token(identifier, "an identifier")
        load_value = self.parse_node()
        return SetNode(
            start_token,
            self._try_get_end_token(),
            identifier.value,
            load_value,
        )

    def parse_set_ptr_node(self, start_token: Token) -> AstNode:
        # (set_ptr identifier expr)
        identifier = self._get_next_token()
        if identifier.token_type != TokenType.IDENTIFIER:
            raise unexpected_token(identifier, "an identifier")
        load_value = self.parse_node()
        return SetPtrNode(
            start_token,
            self._try_get_end_token(),
            identifier.value,
            load_value,
        )

    def parse_defun_node(
        self, start_token: Token, token: Token, is_global: bool = False
    ) -> AstNode:
        # (defun identifier (param_identifier_1 param_identifier_2 ...)
        #   body_expr
        #   body_expr
        #   ...
        # )

        # Only allow function definition in global scope
        if not is_global:
            raise ValueError(
                f"Unexpected function definition at line {token.line} col {token.pos},"
                " function definition is only allowed in the global scope"
            )

        func_id_token = self._get_next_token()
        if func_id_token.token_type != TokenType.IDENTIFIER:
            raise unexpected_token(func_id_token, "a function identifier")

        params_start = self._get_next_token()
        if params_start.token_type != TokenType.LEFT_PARENTHESIS:
            raise unexpected_token(params_start, "(")

        param_ids: list[str] = []

        while self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
            param_token = self._get_next_token()
            if param_token.token_type != TokenType.IDENTIFIER:
                raise unexpected_token(param_token, "a parameter identifier")
            param_ids.append(param_token.value)

        self._get_next_token()  # Consume param closing parenthesis

        body: list[AstNode] = []

        while self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
            body.append(self.parse_node())

        return FuncNode(
            start_token,
            self._try_get_end_token(),
            func_id_token.value,
            param_ids,
            body,
        )

    def parse_alloc_str_node(
        self, start_token: Token, token: Token, is_global: bool = False
    ) -> AstNode:
        # Only allow string buffer allocation in global scope
        if not is_global:
            raise ValueError(
                f"Unexpected string allocation at line {token.line} col {token.pos},"
                " string allocation is only allowed in the global scope"
            )

        str_id = self._get_next_token()
        if str_id.token_type != TokenType.IDENTIFIER:
            raise unexpected_token(str_id, "an identifier")
        size = self._get_next_token()
        if size.token_type != TokenType.INT_LITERAL:
            raise unexpected_token(size, "an integer")
        return StrAllocNode(
            start_token,
            self._try_get_end_token(),
            str_id.value,
            int(size.value),
        )

    def parse_let_node(self, start_token: Token) -> AstNode:
        # (let ((varname expr) (varname expr) ...)
        #   body_expr
        #   body_expr
        #   ...
        # )
        let_vars = self.parse_let_vars()
        let_body: list[AstNode] = []
        while self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
            let_body.append(self.parse_node())
        end_token = self._get_next_token()  # Consume the closing parenthesis
        return LetNode(start_token, end_token, let_vars, let_body)

    def parse_keywords(self, start_token: Token, token: Token, is_global: bool = False) -> AstNode:
        node: AstNode

        if token.value == "let":
            node = self.parse_let_node(start_token)
        elif token.value == "set":
            node = self.parse_set_node(start_token)
        elif token.value == "set_ptr":
            node = self.parse_set_ptr_node(start_token)
        elif token.value == "get_char":
            # (get_char)
            node = GetCharNode(start_token, self._try_get_end_token())
        elif token.value == "put_char":
            # (put_char expr)
            load_value = self.parse_node()
            node = PutCharNode(start_token, self._try_get_end_token(), load_value)
        elif token.value == "loop":
            node = self.parse_loop_node(start_token)
        elif token.value in MathNode.MathOp.__members__.values():
            # (mathop left_operand right_operand)
            math_op = MathNode.MathOp(token.value)
            left_operand = self.parse_node()
            right_opreand = self.parse_node()
            node = MathNode(
                start_token,
                self._try_get_end_token(),
                left_operand,
                right_opreand,
                math_op,
            )
        elif token.value == "defun":
            node = self.parse_defun_node(start_token, token, is_global)
        elif token.value == "if":
            # (if expr true_expr [false_expr])
            condition = self.parse_node()
            true_expr = self.parse_node()
            false_expr = None
            if self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
                false_expr = self.parse_node()
            node = IfNode(
                start_token,
                self._try_get_end_token(),
                condition,
                true_expr,
                false_expr,
            )
        elif token.value == "alloc_str":
            node = self.parse_alloc_str_node(start_token, token, is_global)
        elif token.value == "@":
            # (@ identifier)
            if self._peek_next_token().token_type != TokenType.IDENTIFIER:
                raise unexpected_token(self._peek_next_token(), "an identifier")
            identifier = self._get_next_token()
            node = LoadByPointerIdentifierNode(
                start_token, self._try_get_end_token(), identifier.value
            )
        else:
            # Everything else is assumed to be a function call
            # (func_identifier [params])
            params: list[AstNode] = []

            while self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
                params.append(self.parse_node())

            node = FuncCallNode(start_token, self._get_next_token(), token.value, params)

        return node
    
    def parse_multiple_expressions_node(self, start_token: Token) -> AstNode:
        nodes: list[AstNode] = []
        while self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
            nodes.append(self.parse_node())
        return MultipleExpressionNode(start_token, self._get_next_token(), nodes)

    def parse_node(self, is_global: bool = False) -> AstNode:
        token = self._get_next_token()

        if token.token_type == TokenType.LEFT_PARENTHESIS:
            start_token = token
            if self._peek_next_token().token_type == TokenType.IDENTIFIER:
                return self.parse_keywords(start_token, self._get_next_token(), is_global)
            if self._peek_next_token().token_type == TokenType.LEFT_PARENTHESIS:
                return self.parse_multiple_expressions_node(start_token)
        elif token.token_type == TokenType.BOOL_LITERAL:
            return IntLiteralNode(token, 1 if token.value == "true" else 0)
        elif token.token_type == TokenType.INT_LITERAL:
            return IntLiteralNode(token, int(token.value))
        elif token.token_type == TokenType.STRING_LITERAL:
            return StringLiteralNode(token, token.value)
        elif token.token_type == TokenType.IDENTIFIER:
            return LoadByIdentifierNode(token, token.value)

        raise unexpected_token(token, "dmitrik to write better code")


def build_nodes_from_tokens(tokens: list[Token]):
    builder = AstBuilder(tokens)
    nodes: list[AstNode] = []

    while not builder.is_eof():
        nodes.append(builder.parse_node(True))

    return nodes
