import lexer
import parser
import monkey_object as mobject
from monkey_object import MonkeyObject
import evaluator

def test_eval_integer_expression():
    tests = [
        ("5", 5),
        ("10", 10),
        ("-5", -5),
        ("-10", -10),
        ("5 + 5 + 2", 12),
        ("2 * 2 * 2", 8),
        ("-50 + 100 + -50", 0),
        ("5 + 2 * 10", 25),
        ("50 / 2 * 2 + 10", 60),
        ("(5+10*2+15/3)*2+-10", 50),
    ]

    for input, expected in tests:
        evaluated = eval_test(input)
        integer_object_test(evaluated, expected)

def eval_test(input: str) -> MonkeyObject:
    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()

    return evaluator.eval(program)

def integer_object_test(obj: MonkeyObject, expected: int):
    assert isinstance(obj, mobject.Integer), f"object is not Integer. got {type(obj)}"
    assert obj.value == expected, f"object has the wrong value. got {obj.value}, wanted {expected}"

def test_eval_boolean_expression():
    tests = [
        ("true", True),
        ("false", False),
        ("1 < 2", True),
        ("1 > 2", False),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 > 1", False),
        ("2 != 1", True),
        ("1 < 1", False),
        ("true == true", True),
        ("true != false", True),
        ("false == false", True),
        ("false != true", True),
        ("true == false", False),
        ("true != true", False),
        ("false != false", False),
        ("(1<2) == true", True),
        ("false == (2>1)", False),
    ]

    for input, expected in tests:
        evaluated = eval_test(input)
        boolean_object_test(evaluated, expected)

def boolean_object_test(obj: MonkeyObject, expected: bool):
    assert isinstance(obj, mobject.Boolean), f"object is not Boolean. got {type(obj)}"
    assert obj.value == expected, f"object has the wrong value. got {obj.value}, wanted {expected}"

def test_bang_operator():
    tests = [
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!false", False),
        ("!!5", True),
    ]

    for input, expected in tests:
        evaluated = eval_test(input)
        boolean_object_test(evaluated, expected)