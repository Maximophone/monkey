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
    env = mobject.Environment()

    return evaluator.eval(program, env)

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

def test_if_else_expressions():
    tests = [
        ("if(true){10}", 10),
        ("if(false){10}", None),
        ("if(1){10}", 10),
        ("if(1<2){10}", 10),
        ("if(1>2){10}", None),
        ("if(1>2){10}else{2}", 2),
        ("if(1<2){1}else{2}", 1),
    ]

    for input, expected in tests:
        evaluated = eval_test(input)
        if expected is not None:
            integer_object_test(evaluated, expected)
        else:
            null_object_test(evaluated)

def null_object_test(obj: MonkeyObject):
    return obj == evaluator.NULL

def test_return_statements():
    tests = [
        ("return 10;", 10),
        ("return 10; 9;", 10),
        ("return 2*5; 9;", 10),
        ("9; return 2*5; 9;", 10),
        ("""
        if (true){
            if(true){
                return 1;
            }
            return 2;
        }
        """, 1)
    ]

    for input, expected in tests:
        evaluated = eval_test(input)
        integer_object_test(evaluated, expected)

def test_error_handling():
    tests = [
        ("5 + true", "type mismatch: INTEGER + BOOLEAN"),
        ("5 + true; 5;", "type mismatch: INTEGER + BOOLEAN"),
        ("-true", "unknown operator: -BOOLEAN"),
        ("true + false", "unknown operator: BOOLEAN + BOOLEAN"),
        ("5; true + false; 5;", "unknown operator: BOOLEAN + BOOLEAN"),
        ("if(10>1){true+false;}", "unknown operator: BOOLEAN + BOOLEAN"),
        ("foobar", "identifier not found: foobar")
    ]

    for input, expected in tests:
        evaluated: mobject.Error = eval_test(input)
        assert isinstance(evaluated, mobject.Error), f"no error object returned. got {type(evaluated)}"
        assert evaluated.message == expected, f"wrong error message. expected '{expected}', got '{evaluated.message}'"

def test_let_statements():
    tests = [
        ("let a = 5; a;", 5),
        ("let a = 5*5; a;", 25),
        ("let a = 5; let b = a; b;", 5),
        ("let a=5; let b=a; let c=a + b + 5; c;", 15),
    ]

    for input, expected in tests:
        integer_object_test(eval_test(input), expected)

def test_function_object():
    input = "fn(x){x+2;};"
    expected_body="(x+2)"
    fn: mobject.Function = eval_test(input)

    assert isinstance(fn, mobject.Function), f"object is not Function. got {type(fn)}"
    assert len(fn.parameters) == 1, f"function has wrong number of parameters. parameters = {fn.parameters}"
    assert str(fn.parameters[0]) == "x", f"parameter is not x. got {fn.parameters[0]}"
    assert str(fn.body) == expected_body, f"body is not {expected_body}. got {fn.body}"

def test_function_application():
    tests = [
        ("let identity = fn(x){x;}; identity(5);", 5),
        ("let identity = fn(x){return x;}; identity(5);", 5),
        ("let double = fn(x){x*2;}; double(5);", 10),
        ("let add = fn(x, y){x + y}; add(5, 2);", 7),
    ]
    for input, expected in tests:
        integer_object_test(eval_test(input), expected)

def test_closures():
    input = """
    let newadder = fn(x) {
        fn(y){x + y};
    };
    let addtwo = newadder(2);
    addtwo(2);
    """
    integer_object_test(eval_test(input), 4)