import monkey_ast as ast

from dataclasses import dataclass, field
from typing import Dict, List

INTEGER_OBJ = "INTEGER"
BOOLEAN_OBJ = "BOOLEAN"
STRING_OBJ = "STRING"
NULL_OBJ = "NULL"
RETURN_VALUE_OBJ = "RETURN_VALUE"
ERROR_OBJ = "ERROR"
FUNCTION_OBJ = "FUNCTION"

class ObjectType(str):
    pass

class MonkeyObject:
    @property
    def typ(self) -> ObjectType:
        raise NotImplementedError

    @property
    def inspect(self) -> str:
        raise NotImplementedError


@dataclass
class Integer(MonkeyObject):
    value: int

    @property
    def typ(self) -> ObjectType:
        return INTEGER_OBJ

    @property
    def inspect(self) -> str:
        return str(self.value)

@dataclass
class Boolean(MonkeyObject):
    value: bool

    @property
    def typ(self) -> ObjectType:
        return BOOLEAN_OBJ

    @property
    def inspect(self) -> str:
        return str(self.value).lower()

@dataclass
class String(MonkeyObject):
    value: str

    @property
    def typ(self) -> ObjectType:
        return STRING_OBJ

    @property
    def inspect(self) -> str:
        return self.value

class Null(MonkeyObject):

    @property
    def typ(self) -> ObjectType:
        return NULL_OBJ

    @property
    def inspect(self) -> str:
        return "null"

@dataclass
class ReturnValue(MonkeyObject):
    value: MonkeyObject

    @property
    def typ(self) -> ObjectType:
        return RETURN_VALUE_OBJ

    @property
    def inspect(self) -> str:
        return self.value.inspect()

@dataclass
class Error(MonkeyObject):
    message: str

    @property
    def typ(self) -> ObjectType:
        return ERROR_OBJ

    @property
    def inspect(self) -> str:
        return f"ERROR: {self.message}"

@dataclass
class Environment:
    store: Dict[str, MonkeyObject] = field(default_factory=lambda: {})
    outer: "Environment" = None

    def get(self, name:str) -> MonkeyObject:
        obj = self.store.get(name)
        if obj is None and self.outer is not None:
            return self.outer.get(name)
        return obj

    def set(self, name:str, val: MonkeyObject) -> MonkeyObject:
        self.store[name] = val
        return val

    @staticmethod
    def new_enclosed(outer) -> "Environment":
        env = Environment()
        env.outer = outer
        return env

    

@dataclass
class Function(MonkeyObject):
    parameters: List[ast.Identifier]
    body: ast.BlockStatement
    env: Environment

    @property
    def typ(self) -> ObjectType:
        return FUNCTION_OBJ

    @property
    def inspect(self) -> str:
        params_str = ','.join([str(param) for param in self.parameters]) if self.parameters is not None else ''
        body_str = str(self.body) if self.body is not None else ''
        return f"fn({params_str}){body_str}"