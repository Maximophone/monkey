from dataclasses import dataclass

INTEGER_OBJ = "INTEGER"
BOOLEAN_OBJ = "BOOLEAN"
NULL_OBJ = "NULL"

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