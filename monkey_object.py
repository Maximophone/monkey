from dataclasses import dataclass

INTEGER_OBJ = "INTEGER"
BOOLEAN_OBJ = "BOOLEAN"
NULL_OBJ = "NULL"
RETURN_VALUE_OBJ = "RETURN_VALUE"
ERROR_OBJ = "ERROR"

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