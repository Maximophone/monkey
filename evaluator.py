import monkey_object as mobject
from monkey_object import MonkeyObject, NULL, TRUE, FALSE
import monkey_ast as ast
from monkey_builtins import builtins
from evaluator_utils import new_error, is_error, is_return, is_break, is_continue

from typing import List, Dict


def eval(node: ast.Node, env: mobject.Environment) -> MonkeyObject:
    typ = type(node)
    if typ == ast.Program:
        return eval_program(node, env)
    elif typ == ast.ExpressionStatement:
        return eval(node.expression, env)
    elif typ == ast.IntegerLiteral:
        return mobject.Integer(value=node.value)
    elif typ == ast.Boolean:
        return native_bool_to_boolean_object(node.value)
    elif typ == ast.StringLiteral:
        return mobject.String(value=node.value)
    elif typ == ast.Identifier:
        return eval_identifier(node, env)
    elif typ == ast.PrefixExpression:
        right = eval(node.right, env)
        if is_error(right):
            return right
        return eval_prefix_expression(node.operator, right)
    elif typ == ast.InfixExpression:
        left = eval(node.left, env)
        if is_error(left):
            return left
        right = eval(node.right, env)
        if is_error(right):
            return right
        return eval_infix_expression(node.operator, left, right)
    elif typ == ast.AssignExpression:
        value = eval(node.value, env)
        if is_error(value):
            return value
        val = env.reset(node.name.value, value)
        if val is None:
            return new_error("variable '{}' does not exist. Can't reassign", node.name.value)
        return val
    elif typ == ast.BlockStatement:
        return eval_block_statement(node, env)
    elif typ == ast.IfExpression:
        return eval_if_expression(node, env)
    elif typ == ast.ForExpression:
        return eval_for_expression(node, env)
    elif typ == ast.WhileExpression:
        return eval_while_expression(node, env)
    elif typ == ast.ReturnStatement:
        val = eval(node.return_value, env)
        if is_error(val):
            return val
        return mobject.ReturnValue(val)
    elif typ == ast.BreakStatement:
        return mobject.Break()
    elif typ == ast.ContinueStatement:
        return mobject.Continue()
    elif typ == ast.LetStatement:
        val = eval(node.value, env)
        if is_error(val):
            return val
        env.set(node.name.value, val)
    elif typ == ast.FunctionLiteral:
        params = node.parameters
        body = node.body
        return mobject.Function(parameters=params, body=body, env=env)
    elif typ == ast.CallExpression:
        function = eval(node.function, env)
        if is_error(function):
            return function
        args = eval_expressions(node.arguments, env)
        if len(args) == 1 and is_error(args[0]):
            return args[0]
        return apply_function(function, args)
    elif typ == ast.ArrayLiteral:
        elements = eval_expressions(node.elements, env)
        if len(elements) == 1 and is_error(elements[0]):
            return elements[0]
        return mobject.Array(elements=elements)
    elif typ == ast.IndexExpression:
        left = eval(node.left, env)
        if is_error(left):
            return left
        index = eval(node.index, env)
        if is_error(index):
            return index
        return eval_index_expression(left, index)
    elif typ == ast.HashLiteral:
        return eval_hash_literal(node, env)
    else:
        return NULL

def eval_program(program: ast.Program, env: mobject.Environment) -> MonkeyObject:
    result: MonkeyObject

    for statement in program.statements:
        result = eval(statement, env)
        if result is None:
            continue
        elif result.typ == mobject.RETURN_VALUE_OBJ:
            return result.value
        elif result.typ == mobject.ERROR_OBJ:
            return result
        elif is_break(result):
            return new_error("break cannot be used outside of a loop")
        elif is_continue(result):
            return new_error("continue cannot be used outside of a loop")

    return result

def eval_block_statement(block: ast.BlockStatement, env: mobject.Environment) -> MonkeyObject:
    result: MonkeyObject = NULL

    for statement in block.statements:
        result = eval(statement, env)
        if is_return(result) or is_break(result) or is_continue(result) or is_error(result):
            return result
    return result

def eval_loop_block_statement(block: ast.BlockStatement, env: mobject.Environment) -> MonkeyObject:
    result: MonkeyObject = NULL

    for statement in block.statements:
        result = eval(statement, env)
        if result is None:
            continue
        if result.typ in (mobject.RETURN_VALUE_OBJ, mobject.BREAK_OBJ, mobject.CONTINUE_OBJ, mobject.ERROR_OBJ):
            return result
    return result

def eval_expressions(exps: List[ast.Expression], env: mobject.Environment) -> List[MonkeyObject]:
    result: List[MonkeyObject] = []
    for exp in exps:
        evaluated = eval(exp, env)
        if is_error(evaluated):
            return [evaluated]
        result.append(evaluated)
    return result

def eval_index_expression(left: MonkeyObject, index: MonkeyObject) -> MonkeyObject:
    if left.typ == mobject.ARRAY_OBJ and index.typ == mobject.INTEGER_OBJ:
        return eval_array_index_expression(left, index)
    elif left.typ == mobject.HASH_OBJ:
        if not isinstance(index, mobject.Hashable):
            return new_error("unusable as hash key: {}", index.typ)
        return eval_hash_index_expression(left, index)
    else:
        return new_error("index operator not supported: {}", left.typ)

def eval_array_index_expression(left: mobject.Array, index: mobject.Integer) -> MonkeyObject:
    idx = index.value
    max_idx = len(left.elements) - 1
    if idx < 0 or idx > max_idx:
        return NULL
    return left.elements[idx]

def eval_hash_index_expression(left: mobject.Hash, index: mobject.Hashable) -> MonkeyObject:
    pair = left.pairs.get(index.hash_key)
    if pair is None:
        return NULL
    return pair.value

def eval_hash_literal(node: ast.HashLiteral, env: mobject.Environment) -> MonkeyObject:
    pairs: Dict[mobject.HashKey, mobject.HashPair] = {}

    for key_node, value_node in node.pairs:
        key = eval(key_node, env)
        if is_error(key):
            return key
        if not isinstance(key, mobject.Hashable):
            return new_error("unusable as hash key: {}", key.typ)
        value = eval(value_node, env)
        if is_error(value):
            return value
        
        hashed = key.hash_key
        pairs[hashed] = mobject.HashPair(key=key, value=value)
    
    return mobject.Hash(pairs=pairs)

def eval_identifier(node: ast.Identifier, env: mobject.Environment) -> MonkeyObject:
    val = env.get(node.value)
    if val is not None:
        return val
    builtin = builtins.get(node.value)
    if builtin is not None:
        return builtin
    return new_error("identifier not found: {}", node.value)

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
    elif left.typ == mobject.STRING_OBJ and right.typ == mobject.STRING_OBJ:
        return eval_string_infix_expression(operator, left, right)
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

def eval_string_infix_expression(operator: str, left: MonkeyObject, right: MonkeyObject) -> MonkeyObject:
    if operator != "+":
        return new_error("unknown operator: {} {} {}", left.typ, operator, right.typ)
    return mobject.String(value=left.value + right.value)

def eval_if_expression(exp: ast.IfExpression, env: mobject.Environment) -> MonkeyObject:
    condition = eval(exp.condition, env)
    if is_error(condition):
        return condition
    if is_truthy(condition):
        return eval(exp.consequence, env)
    elif exp.alternative is not None:
        return eval(exp.alternative, env)
    else:
        return NULL

def eval_for_expression(exp: ast.ForExpression, env: mobject.Environment) -> MonkeyObject:
    iterator: mobject.Array = eval(exp.iterator, env)
    if not iterator.typ == mobject.ARRAY_OBJ:
        return new_error("iterator must be ARRAY. found {}", iterator.typ)
    evaluated = NULL
    for value in iterator.elements:
        extended_env = extend_for_body_env(env, exp.element, value)
        evaluated = eval_loop_block_statement(exp.body, extended_env)
        if is_error(evaluated) or is_return(evaluated):
            return evaluated
        if is_break(evaluated):
            return NULL
        if is_continue(evaluated):
            evaluated = NULL
    return evaluated

def eval_while_expression(exp: ast.WhileExpression, env: mobject.Environment) -> MonkeyObject:
    evaluated = NULL
    while True:
        condition = eval(exp.condition, env)
        if is_error(condition):
            return condition
        if not is_truthy(condition):
            return evaluated
        extended_env = mobject.Environment.new_enclosed(env)
        evaluated = eval_loop_block_statement(exp.body, extended_env)
        if is_error(evaluated) or is_return(evaluated):
            return evaluated
        if is_break(evaluated):
            return NULL
        if is_continue(evaluated):
            evaluated = NULL
    return evaluated

def is_truthy(obj: MonkeyObject) -> bool:
    if obj == NULL:
        return False
    elif obj == TRUE:
        return True
    elif obj == FALSE:
        return False
    else:
        return True

def apply_function(fn: MonkeyObject, args: List[MonkeyObject]) -> MonkeyObject:  
    if isinstance(fn, mobject.Function):
        if len(fn.parameters) > len(args):
            return new_error("function call missing required arguments: {}", ', '.join([param.value for param in fn.parameters[len(args):]]))
        extended_env = extend_function_env(fn, args)
        evaluated = eval(fn.body, extended_env)
        return unwrap_return_value(evaluated)
    elif isinstance(fn, mobject.Builtin):
        return fn.fn(*args)
    else:
        return new_error("not a function: {}", fn.typ)

def extend_function_env(fn: mobject.Function, args: List[MonkeyObject]) -> mobject.Environment:
    env = mobject.Environment.new_enclosed(fn.env)
    for i, param in enumerate(fn.parameters):
        env.set(param.value, args[i])
    return env

def extend_for_body_env(env: mobject.Environment, ident: ast.Identifier, value: MonkeyObject) -> mobject.Environment:
    new_env = mobject.Environment.new_enclosed(env)
    new_env.set(ident.value, value)
    return new_env

def unwrap_return_value(obj: MonkeyObject) -> MonkeyObject:
    if isinstance(obj, mobject.ReturnValue):
        return obj.value
    return obj