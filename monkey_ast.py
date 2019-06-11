from typing import NamedTuple, List, Dict, Tuple
from dataclasses import dataclass
import tokens

class Node:
    @property
    def token_literal(self):
        raise NotImplementedError

class Expression(Node):
    def expression_node(self):
        raise NotImplementedError

    @property
    def token_literal(self):
        return self.token.literal

class Statement(Node):
    def statement_node(self):
        raise NotImplementedError

    @property
    def token_literal(self):
        return self.token.literal

@dataclass
class BlockStatement(Node):
    token: tokens.Token
    statements: List[Statement] = None

    @property
    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return "".join([str(statement) for statement in (self.statements if self.statements is not None else [])])

@dataclass
class Identifier(Expression):
    token: tokens.Token
    value: str = None

    def __str__(self):
        return self.value

@dataclass
class IntegerLiteral(Expression):
    token: tokens.Token
    value: int = None

    def __str__(self):
        return self.token.literal

@dataclass
class Boolean(Expression):
    token: tokens.Token
    value: bool = None

    def __str__(self):
        return self.token.literal

@dataclass
class StringLiteral(Expression):
    token: tokens.Token
    value: str = None

    def __str__(self):
        return self.token_literal

@dataclass
class ArrayLiteral(Expression):
    token: tokens.Token
    elements: List[Expression] = None

    def __str__(self):
        return f"[{','.join([str(el) for el in self.elements])}]" if self.elements is not None else "[]"

@dataclass
class IndexExpression(Expression):
    token: tokens.Token
    left: Expression = None
    index: Expression = None

    def __str__(self):
        return f"({str(self.left)}[{str(self.index)}])"

@dataclass
class HashLiteral(Expression):
    token: tokens.Token
    pairs: List[Tuple[Expression, Expression]] = None

    def __str__(self):
        str_pairs = [f"{str(k)}:{str(v)}" for k, v in self.pairs] if self.pairs is not None else []
        return "{" + ", ".join(str_pairs) + "}"

@dataclass
class IfExpression(Expression):
    token: tokens.Token
    condition: Expression = None
    consequence: BlockStatement = None
    alternative: BlockStatement = None

    def __str__(self):
        return f"if{str(self.condition)} {str(self.consequence)}"+(f"else {str(self.alternative)}" if self.alternative is not None else "")

@dataclass
class ForExpression(Expression):
    token: tokens.Token
    iterator: Expression = None
    element: Identifier = None
    body: BlockStatement = None

    def __str__(self):
        return f"for({self.element} in {self.iterator})" + "{" + str(self.body) + "}"

@dataclass
class WhileExpression(Expression):
    token: tokens.Token
    condition: Expression = None
    body: BlockStatement = None

    def __str__(self):
        return f"while({self.condition})" + "{" + str(self.body) + "}"

@dataclass
class FunctionLiteral(Expression):
    token: tokens.Token
    parameters: List[Identifier] = None
    body: BlockStatement = None

    def __str__(self):
        return f"{self.token_literal}({','.join([str(param) for param in (self.parameters if self.parameters is not None else [])])})"+"{"+f"{str(self.body)}"+"}"

@dataclass
class CallExpression(Expression):
    token: tokens.Token
    function: Expression = None
    arguments: List[Expression] = None

    def __str__(self):
        return f"{str(self.function)}({','.join([str(arg) for arg in (self.arguments if self.arguments is not None else [])])})"

@dataclass
class PrefixExpression(Expression):
    token: tokens.Token
    operator: str = None
    right: Expression = None
    
    def __str__(self):
        return f"({self.operator}{str(self.right)})"

@dataclass
class InfixExpression(Expression):
    token: tokens.Token
    left: Expression = None
    operator: str = None
    right: Expression = None

    def __str__(self):
        return f"({str(self.left)}{self.operator}{str(self.right)})"

@dataclass
class AssignExpression(Expression):
    token: tokens.Token
    name: Expression = None
    value: Expression = None

    def __str__(self):
        return f"({self.name}={self.value})"

@dataclass
class LetStatement(Statement):
    token: tokens.Token
    name: Identifier = None
    value: Expression = None

    def __str__(self):
        return f"{self.token_literal} {str(self.name)} = {str(self.value) if self.value is not None else ''};"

@dataclass
class ReturnStatement(Statement):
    token: tokens.Token
    return_value: Expression = None

    def __str__(self):
        return f"{self.token_literal} {str(self.return_value) if self.return_value is not None else ''};"

@dataclass
class BreakStatement(Statement):
    token: tokens.Token

    def __str__(self):
        return self.token_literal + ";"

@dataclass
class ContinueStatement(Statement):
    token: tokens.Token

    def __str__(self):
        return self.token_literal + ";"

@dataclass
class ExpressionStatement(Statement):
    token: tokens.Token
    expression: Expression = None

    def __str__(self):
        return str(self.expression) if self.expression is not None else ''

class Program(Node):
    def __init__(self, statements: List[Statement] = None):
        if statements is None:
            statements = []
        self.statements: List[Statement] = statements

    @property
    def token_literal(self):
        if len(self.statements) > 0:
            return self.statements[0].token_literal
        else:
            return ""

    def __str__(self):
        return "".join([str(statement) for statement in self.statements])
