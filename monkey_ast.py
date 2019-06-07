from typing import NamedTuple, List
from dataclasses import dataclass
import tokens

class Node:
    @property
    def token_literal(self):
        raise NotImplementedError

class Expression(Node):
    def expression_node(self):
        raise NotImplementedError

class Statement(Node):
    def statement_node(self):
        raise NotImplementedError

@dataclass
class Identifier(Expression):
    token: tokens.Token
    value: str = None

    @property
    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return self.value

@dataclass
class IntegerLiteral(Expression):
    token: tokens.Token
    value: int = None

    @property
    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return self.token.literal

@dataclass
class PrefixExpression(Expression):
    token: tokens.Token
    operator: str = None
    right: Expression = None

    @property
    def token_literal(self):
        return self.token.literal
    
    def __str__(self):
        return f"({self.operator}{str(self.right)})"

@dataclass
class InfixExpression(Expression):
    token: tokens.Token
    left: Expression = None
    operator: str = None
    right: Expression = None

    @property
    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return f"({str(self.left)}{self.operator}{str(self.right)})"

@dataclass
class LetStatement(Statement):
    token: tokens.Token
    name: Identifier = None
    value: Expression = None

    @property
    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return f"{self.token_literal} {str(self.name)} = {str(self.value) if self.value is not None else ''};"

@dataclass
class ReturnStatement(Statement):
    token: tokens.Token
    return_value: Expression = None

    @property
    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return f"{self.token_literal} {str(self.return_value) if self.return_value is not None else ''};"

@dataclass
class ExpressionStatement(Statement):
    token: tokens.Token
    expression: Expression = None

    @property
    def token_literal(self):
        return self.token.literal

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
