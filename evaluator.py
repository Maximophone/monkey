import monkey_object as mobject
from monkey_object import MonkeyObject
import monkey_ast as ast

from typing import List

NULL = mobject.Null()
TRUE = mobject.Boolean(value=True)
FALSE = mobject.Boolean(value=False)

def eval(node: ast.Node) -> MonkeyObject:
    typ = type(node)
    if typ == ast.Program:
        return eval_program(node)
    elif typ == ast.ExpressionStatement:
        return eval(node.expression)
    elif typ == ast.IntegerLiteral:
        return mobject.Integer(value=node.value)
    elif typ == ast.Boolean:
        return native_bool_to_boolean_object(node.value)
    elif typ == ast.PrefixExpression:
        right = eval(node.right)
        if is_error(right):
            return right
        return eval_prefix_expression(node.operator, right)
    elif typ == ast.InfixExpression:
        left = eval(node.left)
        if is_error(left):
            return left
        right = eval(node.right)
        if is_error(right):
            return right
        return eval_infix_expression(node.operator, left, right)
    elif typ == ast.BlockStatement:
        return eval_block_statement(node)
    elif typ == ast.IfExpression:
        return eval_if_expression(node)
    elif typ == ast.ReturnStatement:
        val = eval(node.return_value)
        if is_error(val):
            return val
        return mobject.ReturnValue(val)
    else:
        return NULL

def eval_program(program: ast.Program) -> MonkeyObject:
    result: MonkeyObject

    for statement in program.statements:
        result = eval(statement)
        if result is None:
            continue
        elif result.typ == mobject.RETURN_VALUE_OBJ:
            return result.value
        elif result.typ == mobject.ERROR_OBJ:
            return result

    return result

def eval_block_statement(block: ast.BlockStatement) -> MonkeyObject:
    result: MonkeyObject

    for statement in block.statements:
        result = eval(statement)
        if result is not None and result.typ == mobject.RETURN_VALUE_OBJ or result.typ == mobject.ERROR_OBJ:
            return result
    return result

def native_bool_to_boolean_object(value: bool) -> mobject.Boolean:
    return TRUE if value else FALSE

def eval_prefix_expression(operator: str, right: MonkeyObject) -> MonkeyObject:
    if operator == "!":
        return eval_bang_operator_expression(right)
    elif operator == "-":
        return eval_minus_prefix_operator_expression(right)
    else:
        return new_error("unknown operator: {operator}{typ}", operator=operator, typ=right.typ)

def eval_bang_operator_expression(right: MonkeyObject) -> MonkeyObject:
    if right == TRUE:
        return FALSE
    elif right == FALSE:
        return TRUE
    elif right == NULL:
        return TRUE
    else:
        return FALSE

def eval_minus_prefix_operator_expression(right: MonkeyObject) -> MonkeyObject:
    if right.typ != mobject.INTEGER_OBJ:
        return new_error("unknown operator: -{}", right.typ)
    
    return mobject.Integer(value=-right.value)

def eval_infix_expression(operator: str, left: MonkeyObject, right: MonkeyObject) -> MonkeyObject:
    if left.typ == mobject.INTEGER_OBJ and right.typ == mobject.INTEGER_OBJ:
        return eval_integer_infix_expression(operator, left, right)
    elif left.typ == mobject.BOOLEAN_OBJ and right.typ == mobject.BOOLEAN_OBJ:
        if operator == "==":
            return native_bool_to_boolean_object(left == right)
        elif operator == "!=":
            return native_bool_to_boolean_object(left != right)
        else:
            return new_error("unknown operator: {} {} {}", left.typ, operator, right.typ)
    else:
        return new_error("type mismatch: {} {} {}", left.typ, operator, right.typ)

def eval_integer_infix_expression(operator: str, left: MonkeyObject, right: MonkeyObject) -> MonkeyObject:
    if operator == "+":
        return mobject.Integer(value=left.value+right.value)
    elif operator == "-":
        return mobject.Integer(value=left.value-right.value)
    elif operator == "*":
        return mobject.Integer(value=left.value*right.value)
    elif operator == "/":
        return mobject.Integer(value=left.value//right.value)
    elif operator == "<":
        return native_bool_to_boolean_object(left.value < right.value)
    elif operator == ">":
        return native_bool_to_boolean_object(left.value > right.value)
    elif operator == "!=":
        return native_bool_to_boolean_object(left.value != right.value)
    elif operator == "==":
        return native_bool_to_boolean_object(left.value == right.value)
    else:
        return new_error("unknown operator: {} {} {}", left.typ, operator, right.typ)

def eval_if_expression(exp: ast.IfExpression) -> MonkeyObject:
    condition = eval(exp.condition)
    if is_error(condition):
        return condition
    if is_truthy(condition):
        return eval(exp.consequence)
    elif exp.alternative is not None:
        return eval(exp.alternative)
    else:
        return NULL

def is_truthy(obj: MonkeyObject) -> bool:
    if obj == NULL:
        return False
    elif obj == TRUE:
        return True
    elif obj == FALSE:
        return False
    else:
        return True

def new_error(fmt: str, *args, **kwargs) -> mobject.Error:
    return mobject.Error(fmt.format(*args, **kwargs))

def is_error(obj: MonkeyObject) -> bool:
    if obj is not None:
        return obj.typ == mobject.ERROR_OBJ
    return False