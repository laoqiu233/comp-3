from enum import Enum
from lexer import TokenType, Token, Lexer
from abc import abstractmethod, ABC
from typing import Optional

class AstBackend(ABC):
    pass

class AstNode(ABC):
    @abstractmethod
    def compile(self, backend: AstBackend):
        pass

class LetVarNode(AstNode):
    def __init__(self, identifier: str, load_value: AstNode):
        self.identifier = identifier
        self.load_value = load_value

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        return f'''{self.identifier} = {self.load_value}'''
        

class LetNode(AstNode):
    def __init__(self, start_token: Token, end_token: Token, vars: list[LetVarNode], body: list[AstNode]):
        self.start_token = start_token
        self.end_token = end_token
        self.vars = vars
        self.body = body

    def append_node(self, node: AstNode):
        self.body.append(node)

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        s = f'''(
\tlet ({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tvars:\n'''
        for var in self.vars:
            s += '\t\t' + '\t\t'.join(str(var).splitlines(True)) + '\n'
        s += '\tbody:\n'
        for expr in self.body:
            s += '\t\t' + '\t\t'.join(str(expr).splitlines(True)) + '\n'
        s += '\n)'

        return s

class SetNode(AstNode):
    def __init__(self, start_token: Token, end_token: Token, identifier: str, load_value: AstNode):
        self.start_token = start_token
        self.end_token = end_token
        self.identifier = identifier
        self.load_value = load_value

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        return f'''(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tset
\t{self.identifier}
\tto\n\t''' + '\t'.join(str(self.load_value).splitlines(True)) + '\n)'

class LoopWhileNode(AstNode):
    def __init__(self, start_token: Token, end_token: Token, loop_condition: AstNode, body: list[AstNode]):
        self.start_token = start_token
        self.end_token = end_token
        self.loop_condition = loop_condition
        self.body = body

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        s = f'''(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tloop while\n'''
        s += '\t\t' + '\t\t'.join(str(self.loop_condition).splitlines(True)) + '\n\tdo\n'

        for expr in self.body:
            s += '\t\t' + '\t\t'.join(str(expr).splitlines(True)) + '\n'
        s += ')'
        return s

class GetCharNode(AstNode):
    def __init__(self, start_token: Token, end_token: Token):
        self.start_token = start_token
        self.end_token = end_token

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        return f'get_char ({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})'

class PutCharNode(AstNode):
    def __init__(self, start_token: Token, end_token: Token, load_value: AstNode):
        self.start_token = start_token
        self.end_token = end_token
        self.load_value = load_value

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        return f'''(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tput_char\n\t''' + '\t'.join(str(self.load_value).splitlines(True)) + '\n)'

class MathNode(AstNode):
    class MathOp(str, Enum):
        ADD = '+'
        SUB = '-'
        AND = '&'
        OR  = '|'
        LT  = '<'
        LE  = '<='
        GT  = '>'
        GE  = '>='
        EQ  = '='
        NE  = '!='

    def __init__(self, start_token: Token, end_token: Token, left_operand: AstNode, right_operand: AstNode, op: MathOp):
        self.start_token = start_token
        self.end_token = end_token
        self.left_operand = left_operand
        self.right_operand = right_operand
        self.op = op

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        s = f'''(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\t'''
        s += '\t'.join(str(self.left_operand).splitlines(True))
        s += f'\n\t{self.op.value}\n\t'
        s += '\t'.join(str(self.right_operand).splitlines(True))
        s += '\n)'

        return s
    
class FuncNode(AstNode):
    def __init__(self, start_token: Token, end_token: Token, identifier: str, param_identifiers: list[str], body: list[AstNode]):
        self.start_token = start_token
        self.end_token = end_token
        self.identifier = identifier
        self.param_identifiers = param_identifiers
        self.body = body

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        s = f'function {self.identifier} ({", ".join(self.param_identifiers)}) ({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos}) (\n'

        for expr in self.body:
            s += '\t' + '\t'.join(str(expr).splitlines(True)) + '\n'

        s += ')'

        return s

class IfNode(AstNode):
    def __init__(self, start_token: Token, end_token: Token, if_condition: AstNode, true_expr: AstNode, false_expr: Optional[AstNode]):
        self.start_token = start_token
        self.end_token = end_token
        self.if_condition = if_condition
        self.true_expr = true_expr
        self.false_expr = false_expr

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        s =  f'''(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tif\n\t\t'''
        s += '\t\t'.join(str(self.if_condition).splitlines(True))
        s += '\n\tthen\n\t\t'
        s += '\t\t'.join(str(self.true_expr).splitlines(True))
        if self.false_expr is not None:
            s += '\n\telse\n\t\t'
            s += '\t\t'.join(str(self.false_expr).splitlines(True))
        s += '\n)'
        return s

class FuncCallNode(AstNode):
    def __init__(self, start_token: Token, end_token: Token, func_identifier: str, params: list[AstNode]):
        self.start_token = start_token
        self.end_token = end_token
        self.func_identifier = func_identifier
        self.params = params

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        s = f'''(
\t({self.start_token.line}-{self.start_token.pos} to {self.end_token.line}-{self.end_token.pos})
\tcall {self.func_identifier}
\t(\n
'''
        for param in self.params:
            s += '\t\t' + '\t\t'.join(str(param).splitlines(True)) + '\n'
        
        s += '\t)\n)'

        return s

class IntLiteralNode(AstNode):
    def __init__(self, token: Token, value: int):
        self.token = token
        self.value = value

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        return str(self.value)

class StringLiteralNode(AstNode):
    def __init__(self, token: Token, value: str):
        self.token = token
        self.value = value

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        return f'"{self.value}"'

class LoadByIdentifierNode(AstNode):
    def __init__(self, token: Token, identifier: str):
        self.token = token
        self.identifier = identifier

    def compile(self, backend: AstBackend):
        pass

    def __str__(self) -> str:
        return f'({self.identifier})'

def unexpected_eof(token: Token) -> ValueError:
    return ValueError(f'Unexpected EOF reached at line {token.line} col {token.pos + len(token.value)}')

def unexpected_token(token: Token, expected: str) -> ValueError:
    return ValueError(f'Unexpected token {token.value} at line {token.line} col {token.pos}, expected {expected}')

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

    def _parse_let_vars(self) -> list[LetVarNode]:
        let_vars: list[LetVarNode] = []
        token = self._get_next_token()

        if token.token_type != TokenType.LEFT_PARENTHESIS:
            raise unexpected_token(token, '(')
        
        while (token := self._get_next_token()).token_type != TokenType.RIGHT_PARENTHESIS:
            if token.token_type != TokenType.LEFT_PARENTHESIS:
                raise unexpected_token(token, '( for new variable or ) for closing let block')
            identifier_token = self._get_next_token()
            if identifier_token.token_type != TokenType.IDENTIFIER:
                raise unexpected_token(token, 'an identifier for the variable')
            load_value = self.parse_node()
            
            if (closing_token := self._get_next_token()).token_type != TokenType.RIGHT_PARENTHESIS:
                raise unexpected_token(closing_token, ')')
            
            let_vars.append(LetVarNode(identifier_token.value, load_value))

        return let_vars
    
    def _try_get_end_token(self) -> Token:
        end_token = self._get_next_token()
        if end_token.token_type != TokenType.RIGHT_PARENTHESIS:
            raise unexpected_token(end_token, ')')
        return end_token

    def parse_node(self, is_global: bool = False) -> AstNode:
        token = self._get_next_token()

        if token.token_type == TokenType.LEFT_PARENTHESIS:
            start_token = token
            if (token := self._get_next_token()).token_type == TokenType.IDENTIFIER:
                if token.value == 'let':
                    # (let ((varname expr) (varname expr) ...)
                    #   body_expr
                    #   body_expr
                    #   ...
                    # )
                    let_vars = self._parse_let_vars()
                    let_body: list[AstNode] = []
                    while self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
                        let_body.append(self.parse_node())
                    end_token = self._get_next_token() # Consume the closing parenthesis
                    return LetNode(start_token, end_token, let_vars, let_body)
                elif token.value == 'set':
                    # (set identifier expr)
                    identifier = self._get_next_token()
                    if identifier.token_type != TokenType.IDENTIFIER:
                        raise unexpected_token(identifier, 'an identifier')
                    load_value = self.parse_node()
                    return SetNode(start_token, self._try_get_end_token(), identifier.value, load_value)
                elif token.value == 'get_char':
                    # (get_char)
                    return GetCharNode(start_token, self._try_get_end_token())
                elif token.value == 'put_char':
                    # (put_char expr)
                    load_value = self.parse_node()
                    return PutCharNode(start_token, self._try_get_end_token(), load_value)
                elif token.value == 'loop':
                    loop_op = self._get_next_token()
                    if loop_op.token_type != TokenType.IDENTIFIER:
                        raise unexpected_token(loop_op, 'while or for')
                    if loop_op.value == 'while':
                        # (loop while expr do 
                        #   body_expr
                        #   body_expr
                        #   ...
                        # )
                        loop_condition = self.parse_node()
                        do_token = self._get_next_token()
                        if do_token.token_type != TokenType.IDENTIFIER or do_token.value != 'do':
                            raise unexpected_token(do_token, 'do')
                        body: list[AstNode] = []
                        while self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
                            body.append(self.parse_node())
                        end_token = self._get_next_token()
                        return LoopWhileNode(start_token, end_token, loop_condition, body)
                elif token.value in MathNode.MathOp.__members__.values():
                    # (mathop left_operand right_operand)
                    math_op = MathNode.MathOp(token.value)
                    left_operand = self.parse_node()
                    right_opreand = self.parse_node()
                    return MathNode(start_token, self._try_get_end_token(), left_operand, right_opreand, math_op)
                elif token.value == 'defun':
                    # (defun identifier (param_identifier_1 param_identifier_2 ...) 
                    #   body_expr
                    #   body_expr
                    #   ...
                    # )
                    
                    # Only allow function definition in global scope
                    if not is_global:
                        raise ValueError(f'Unexpected function definition at line {token.line} col {token.pos}, function definition is only allowed in the global scope')
                    
                    func_id_token = self._get_next_token()
                    if func_id_token.token_type != TokenType.IDENTIFIER:
                        raise unexpected_token(func_id_token, 'a function identifier')
                    
                    params_start = self._get_next_token()
                    if params_start.token_type != TokenType.LEFT_PARENTHESIS:
                        raise unexpected_token(params_start, '(')
                    
                    param_ids: list[str] = []

                    while self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
                        param_token = self._get_next_token()
                        if param_token.token_type != TokenType.IDENTIFIER:
                            raise unexpected_token(param_token, 'a parameter identifier')
                        param_ids.append(param_token.value)

                    self._get_next_token() # Consume param closing parenthesis
                    
                    body: list[AstNode] = []

                    while self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
                        body.append(self.parse_node())
                    
                    return FuncNode(start_token, self._try_get_end_token(), func_id_token.value, param_ids, body)
                elif token.value == 'if':
                    # (if expr true_expr [false_expr])
                    condition = self.parse_node()
                    true_expr = self.parse_node()
                    false_expr = None
                    if self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
                        false_expr = self.parse_node()
                    return IfNode(start_token, self._try_get_end_token(), condition, true_expr, false_expr)
                else:
                    # (func_identifier [params])
                    params: list[AstNode] = []

                    while self._peek_next_token().token_type != TokenType.RIGHT_PARENTHESIS:
                        params.append(self.parse_node())

                    return FuncCallNode(start_token, self._get_next_token(), token.value, params)

        elif token.token_type == TokenType.BOOL_LITERAL:
            if token.value == 'false':
                return IntLiteralNode(token, 0)
            else:
                return IntLiteralNode(token, 1)
        elif token.token_type == TokenType.INT_LITERAL:
            return IntLiteralNode(token, int(token.value))
        elif token.token_type == TokenType.STRING_LITERAL:
            return StringLiteralNode(token, token.value)
        elif token.token_type == TokenType.IDENTIFIER:
            return LoadByIdentifierNode(token, token.value)

        raise unexpected_token(token, 'dmitrik to write better code')            

if __name__ == '__main__':
    with open("examples/euler_problem.lisq") as file:
        lexer = Lexer(file)
        tokens = lexer.lex()
        builder = AstBuilder(tokens)

        nodes: list[AstNode] = []
        
        while not builder.is_eof():
            node = builder.parse_node(True)
            nodes.append(node)

        print(*nodes, sep='\n\n')