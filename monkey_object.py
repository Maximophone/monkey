import monkey_ast as ast

from dataclasses import dataclass, field
from typing import Dict, List, Callable, NamedTuple

INTEGER_OBJ = "INTEGER"
BOOLEAN_OBJ = "BOOLEAN"
STRING_OBJ = "STRING"
NULL_OBJ = "NULL"
RETURN_VALUE_OBJ = "RETURN_VALUE"
ERROR_OBJ = "ERROR"
FUNCTION_OBJ = "FUNCTION"
BUILTIN_OBJ = "BUILTIN"
ARRAY_OBJ = "ARRAY"
HASH_OBJ = "HASH"
BREAK_OBJ = "BREAK"
CONTINUE_OBJ = "CONTINUE"

class ObjectType(str):
    pass

class MonkeyObject:
    @property
    def typ(self) -> ObjectType:
        raise NotImplementedError

    @property
    def inspect(self) -> str:
        raise NotImplementedError

class HashKey(NamedTuple):
    typ: ObjectType
    value: int

class HashPair(NamedTuple):
    key: MonkeyObject
    value: MonkeyObject

class Hashable(MonkeyObject):
    @property
    def hash_key(self) -> HashKey:
        raise NotImplementedError

@dataclass
class Integer(Hashable):
    value: int

    @property
    def typ(self) -> ObjectType:
        return INTEGER_OBJ

    @property
    def inspect(self) -> str:
        return str(self.value)

    @property
    def hash_key(self) -> HashKey:
        return HashKey(self.typ, self.value)

@dataclass
class Boolean(Hashable):
    value: bool

    @property
    def typ(self) -> ObjectType:
        return BOOLEAN_OBJ

    @property
    def inspect(self) -> str:
        return str(self.value).lower()

    @property
    def hash_key(self) -> HashKey:
        return HashKey(self.typ, int(self.value))

@dataclass
class String(Hashable):
    value: str

    @property
    def typ(self) -> ObjectType:
        return STRING_OBJ

    @property
    def inspect(self) -> str:
        return f'"{self.value}"'

    @property
    def hash_key(self) -> HashKey:
        return HashKey(self.typ, self.value.__hash__())

@dataclass
class Array(MonkeyObject):
    elements: List[MonkeyObject]

    @property
    def typ(self) -> ObjectType:
        return ARRAY_OBJ
    
    @property
    def inspect(self) -> str:
        return f"[{', '.join([el.inspect for el in self.elements])}]" if self.elements else "[]"

@dataclass
class Hash(MonkeyObject):
    pairs: Dict[HashKey, HashPair]

    @property
    def typ(self) -> ObjectType:
        return HASH_OBJ

    @property
    def inspect(self) -> str:
        pairs_str = [f"{pair.key.inspect}: {pair.value.inspect}" for _, pair in self.pairs.items()]
        return "{"+", ".join(pairs_str)+"}"

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
class Break(MonkeyObject):

    @property
    def typ(self) -> ObjectType:
        return BREAK_OBJ

    @property
    def inspect(self) -> str:
        return "break"

@dataclass
class Continue(MonkeyObject):
    @property
    def typ(self) -> ObjectType:
        return CONTINUE_OBJ
    
    @property
    def inspect(self) -> str:
        return "continue"

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

    def reset(self, name:str, val: MonkeyObject) -> MonkeyObject:
        exists = name in self.store
        if exists:
            return self.set(name, val)
        if self.outer is not None:
            return self.outer.reset(name, val)
        elif self.outer is None:
            return

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

@dataclass
class Builtin(MonkeyObject):
    fn: Callable

    @property
    def typ(self) -> ObjectType:
        return BUILTIN_OBJ

    @property
    def inspect(self) -> str:
        return "builtin function"

NULL = Null()
TRUE = Boolean(value=True)
FALSE = Boolean(value=False)