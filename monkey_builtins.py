import monkey_object as mobject
from monkey_object import MonkeyObject, NULL
from typing import Dict
from evaluator_utils import new_error


def len_builtin(*args) -> mobject.Integer:
    if len(args) != 1:
        return new_error("wrong number of arguments. got {}, want 1", len(args))
    if isinstance(args[0], mobject.String):
        return mobject.Integer(value=len(args[0].value))
    else:
        return new_error("argument to 'len' not supported, got {}", args[0].typ)


builtins: Dict[str, mobject.Builtin] = {
    "len": mobject.Builtin(
        fn=len_builtin
    )
}