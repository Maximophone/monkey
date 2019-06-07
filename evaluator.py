import monkey_object as mobject
from monkey_object import MonkeyObject
import monkey_ast as ast

from typing import List

NULL = mobject.Null()
TRUE = mobject.Boolean(value=True)
FALSE = mobject.Boolean(value=False)

def eval(node: ast.Node) -> MonkeyObject:
    node_to_object = {
        ast.Program: lambda node: eval_statements(node.statements),
        ast.ExpressionStatement: lambda node: eval(node.expression),
        ast.IntegerLiteral: lambda node: mobject.Integer(value=node.value),
        ast.Boolean: lambda node: native_bool_to_boolean_object(node.value),
        ast.PrefixExpression: lambda node: eval_prefix_expression(node.operator, eval(node.right)),
        ast.InfixExpression: lambda node: eval_infix_expression(node.operator, eval(node.left), eval(node.right)),
    }

    return node_to_object.get(type(node), lambda node: NULL)(node)

def eval_statements(statements: List[ast.Statement]) -> MonkeyObject:
    result: MonkeyObject

    for statement in statements:
        result = eval(statement)

    return result

def native_bool_to_boolean_object(value: bool) -> mobject.Boolean:
    return TRUE if value else FALSE

def eval_prefix_expression(operator: str, right: MonkeyObject) -> MonkeyObject:
    if operator == "!":
        return eval_bang_operator_expression(right)
    elif operator == "-":
        return eval_minus_prefix_operator_expression(right)
    else:
        return None

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
        return NULL
    
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
            return NULL
    else:
        return NULL

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
        return NULL