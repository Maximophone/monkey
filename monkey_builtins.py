import monkey_object as mobject
from monkey_object import MonkeyObject, NULL
from typing import Dict
from evaluator_utils import new_error

def check_args_len(args, n) -> mobject.Error:
    if len(args) != n:
        return new_error("wrong number of arguments. got {}, want {}", len(args), n)
    return None


def len_builtin(*args) -> mobject.Integer:
    err = check_args_len(args, 1)
    if err is not None:
        return err
    if isinstance(args[0], mobject.String):
        return mobject.Integer(value=len(args[0].value))
    elif isinstance(args[0], mobject.Array):
        return mobject.Integer(value=len(args[0].elements))
    else:
        return new_error("argument to 'len' not supported, got {}", args[0].typ)

def first(*args) -> MonkeyObject:
    err = check_args_len(args, 1)
    if err is not None: 
        return err
    arg = args[0]
    if arg.typ != mobject.ARRAY_OBJ:
        return new_error("argument to 'first' must be ARRAY, got {}", arg.typ)
    if len(arg.elements) > 0:
        return arg.elements[0]
    return NULL

def last(*args) -> MonkeyObject:
    err = check_args_len(args, 1)
    if err is not None:
        return err
    arg = args[0]
    if arg.typ != mobject.ARRAY_OBJ:
        return new_error("argument to 'last' must be ARRAY, got {}", arg.typ)
    if len(arg.elements) > 0:
        return arg.elements[-1]
    return NULL

def rest(*args) -> mobject.Array:
    err = check_args_len(args, 1)
    if err is not None:
        return err
    arg = args[0]
    if arg.typ != mobject.ARRAY_OBJ:
        return new_error("argument to 'last' must be ARRAY, got {}", arg.typ)
    if len(arg.elements) > 0:
        return mobject.Array(
            elements = arg.elements[1:]
        )
    return NULL

def check_single_arg(typ):
    def closure(f):
        def inner(*args):
            err = check_args_len(args, 1)
            if err is not None:
                return err
            arg = args[0]
            if arg.typ != typ:
                return new_error("argument must be {}, got {}", typ, arg.typ)
            return f(arg)
        return inner
    return closure

def check_args(*typs):
    def closure(f):
        def inner(*args):
            err = check_args_len(args, len(typs))
            if err is not None:
                return err
            for arg, typ in zip(args, typs):
                if typ is not None and arg.typ != typ:
                    return new_error("wrong argument type")
            return f(*args)
        return inner
    return closure

@check_args(mobject.ARRAY_OBJ, None)
def push(array: mobject.Array, obj: MonkeyObject) -> mobject.Array:
    return mobject.Array(elements=array.elements+[obj])

builtins: Dict[str, mobject.Builtin] = {
    "len": mobject.Builtin(
        fn=len_builtin
    ),
    "first": mobject.Builtin(fn=first),
    "last": mobject.Builtin(fn=last),
    "rest": mobject.Builtin(fn=rest),
    "push": mobject.Builtin(fn=push),
}