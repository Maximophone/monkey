from monkey_object import MonkeyObject
import monkey_object as mobject

def new_error(fmt: str, *args, **kwargs) -> mobject.Error:
    return mobject.Error(fmt.format(*args, **kwargs))

def is_error(obj: MonkeyObject) -> bool:
    if obj is not None:
        return obj.typ == mobject.ERROR_OBJ
    return False
