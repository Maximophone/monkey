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
        ("let a = 2; a = 3;", 3),
        ("let a = 5; 5+10*(a=2);", 25),
        ("let a = 3; let f = fn(){a=1;}; f(); a;", 1)
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

def string_object_test(obj: MonkeyObject, expected: str):
    assert isinstance(obj, mobject.String), f"object is not String. got {type(obj)}"
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

def test_for_expressions():
    tests = [
        ("for(x in []){1}", None),
        ("for(x in [1,2,3]){x;}", 3),
    ]

    for input, expected in tests:
        evaluated = eval_test(input)
        if expected is not None:
            integer_object_test(evaluated, expected)
        else:
            null_object_test(evaluated)

def test_while_expressions():
    tests = [
        ("let i = 2; while(i>0){i = i-1; i;}", 0),
        ("while(false){2;}", None),
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
        ("foobar", "identifier not found: foobar"),
        ('"hello" - "world"', "unknown operator: STRING - STRING"),
        ('fn(x,y){}()', "function call missing required arguments: x, y"),
        ('fn(x,y,z){}(2)', "function call missing required arguments: y, z"),
        ('{"name": "monkey"}[fn(x){x}];', "unusable as hash key: FUNCTION"),
        ("a = 3;", "variable 'a' does not exist. Can't reassign"),
        ("8 * (x=2);", "variable 'x' does not exist. Can't reassign"),
    ]

    for input, expected in tests:
        evaluated: mobject.Error = eval_test(input)
        error_test(evaluated, expected)
        assert isinstance(evaluated, mobject.Error), f"no error object returned. got {type(evaluated)}"
        assert evaluated.message == expected, f"wrong error message. expected '{expected}', got '{evaluated.message}'"

def error_test(obj: MonkeyObject, error_string: str):
    assert isinstance(obj, mobject.Error), f"no error object returned. got {type(obj)}"
    assert obj.message == error_string, f"wrong error message. expected '{error_string}', got '{obj.message}'"

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
        ("fn(){}();", None),
    ]
    for input, expected in tests:
        if expected is not None:
            integer_object_test(eval_test(input), expected)
        else:
            null_object_test(eval_test(input))

def test_closures():
    input = """
    let new_adder = fn(x) {
        fn(y){x + y};
    };
    let add_two = new_adder(2);
    add_two(2);
    """
    integer_object_test(eval_test(input), 4)

def test_string_literal():
    input = '"Hello World!"'
    evaluated = eval_test(input)

    assert isinstance(evaluated, mobject.String), f"object is not String. got {type(evaluated)}"
    assert evaluated.value == "Hello World!", f"String has wrong value. got {evaluated.value}"

def test_string_concatenation():
    input = '"Hello " + "World!"'
    string = eval_test(input)

    string_object_test(string, "Hello World!")

def test_builtin_functions():
    tests = [
        ('len("")', 0),
        ('len("four")', 4),
        ('len("hello world")', 11),
        ('len(1)', "argument to 'len' not supported, got INTEGER"),
        ('len("one", "two")', "wrong number of arguments. got 2, want 1"),
        ('len([1, 2, 3])', 3),
        ('let a = [1, 2]; len(a);', 2),
        ('first([1,2])', 1),
        ('last([1,2,3])', 3),
        ('rest([1, 2, 3])', (2, 3)),
        ('push([1,2], 3)', (1, 2, 3)),
        ('range(5)', (0, 1, 2, 3, 4)),
        ('range(0)', ()),
        ('range(-1)', ()),
    ]

    for input, expected in tests:
        evaluated = eval_test(input)
        if type(expected) == int:
            integer_object_test(evaluated, expected)
        elif type(expected) == str:
            error_test(evaluated, expected)
        elif type(expected) == tuple:
            assert type(evaluated) == mobject.Array, f"object is not Array. got {type(evaluated)}"
            for i, exp in enumerate(expected):
                integer_object_test(evaluated.elements[i], exp)

def test_array_literal():
    input = "[1, 2*2, 3+3]"
    evaluated = eval_test(input)

    assert type(evaluated) == mobject.Array, f"object is not Array. got {type(evaluated)}"
    assert len(evaluated.elements) == 3, f"array has wrong number of elements. got {len(evaluated.elements)}"
    integer_object_test(evaluated.elements[0], 1)
    integer_object_test(evaluated.elements[1], 4)
    integer_object_test(evaluated.elements[2], 6)

def test_array_index_expressions():
    tests = [
        ("[1, 2, 3][0]", 1),
        ("[1, 2, 3][1]", 2),
        ("[1, 3, 8][2]", 8),
        ("let i = 0; [1][i]", 1),
        ("[1, 2, 3][1+1]", 3),
        ("let my_array = [1, 2, 3]; my_array[2]", 3),
        ("[1, 2, 3][3]", None),
        ("[1, 2, 3][-1]", None),
    ]

    for input, expected in tests:
        evaluated = eval_test(input)
        if type(expected) == int:
            integer_object_test(evaluated, expected)
        else:
            null_object_test(evaluated)

def test_hash_literals():
    input = """
    let two = "two";
    {
        "one": 10 - 9,
        two: 1 + 1,
        "thr" + "ee": 6/2,
        4: 4,
        true: 5,
        false: 6
    }
    """

    expected = {
        mobject.String(value="one").hash_key: 1,
        mobject.String(value="two").hash_key: 2,
        mobject.String(value="three").hash_key: 3,
        mobject.Integer(value=4).hash_key: 4,
        mobject.Boolean(value=True).hash_key: 5,
        mobject.Boolean(value=False).hash_key: 6
    }

    evaluated = eval_test(input)
    assert type(evaluated) == mobject.Hash, f"object is not Hash, got {type(evaluated)}"
    assert len(evaluated.pairs) == len(expected), f"hash has wrong number of pairs. got {len(evaluated.pairs)}, want {len(expected)}"

    for k, v in expected.items():
        pair = evaluated.pairs.get(k)
        assert pair is not None, f"no pair for key {k} can be found in hash"
        integer_object_test(pair.value, v)

def test_hash_index_expressions():
    tests = [
        ('{"foo": 5}["foo"]', 5),
        ('{"foo": 5}["bar"]', None),
        ('let key = "foo"; {"foo": 5}[key]', 5),
        ('{}["foo"]', None),
        ('{5: 5}[5]', 5),
        ('{true: 6}[true]', 6),
        ('{false: 2}[false]', None)
    ]

    for input, expected in tests:
        evaluated = eval_test(input)
        if type(expected) == int:
            integer_object_test(evaluated, expected)
        else:
            null_object_test(evaluated)