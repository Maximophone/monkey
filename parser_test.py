import lexer
import monkey_ast as ast
import parser
from typing import Any


def test_let_statements():
    tests = [
        ("let x = 5;", "x", 5),
        ("let y = true", "y", True),
        ("let foobar = y", "foobar", "y")
    ]
    
    for input, expected_ident, expected_value in tests:
        program = get_program(input, 1)

        statement = program.statements[0]
        let_statement_test(statement, expected_ident)
        literal_expression_test(statement.value, expected_value)

def test_return_statements():
    tests = [
        ("return 5;", 5),
        ("return true", True),
        ("return y", "y")
    ]

    for input, expected_value in tests:
        program = get_program(input, 1)

        statement: ast.ReturnStatement = program.statements[0]
        check_statement(statement, ast.ReturnStatement)

        literal_expression_test(statement.return_value, expected_value)

def let_statement_test(s, name):
    assert s.token_literal == "let", f"statement token_literal not 'let'. got {s.token_literal}"
    assert isinstance(s, ast.LetStatement), f"statement is not a LetStatement. got {type(s)}"
    assert s.name.value == name, f"statement.name.value not {name}. got {s.name.value}"
    assert s.name.token_literal == name, f"statement.name not {name}. got {s.name.token_literal}"


def check_parser_errors(p: parser.Parser):
    errors = p.errors
    if len(errors) == 0:
        return

    print(f"parser had {len(errors)} errors")
    for error in errors:
        print(f"parser error: {error}")

    raise Exception("Parser Errors")

def check_program_length(program: ast.Program, n: int):
    assert program is not None, f"parse_program() returned None"
    assert len(program.statements) == n, f"program.statements does not contain {n} statements, got {len(program.statements)}"

def check_statement(statement: ast.Statement, typ: Any, literal: str = None):
    assert isinstance(statement, typ), f"statement is not a {typ}. got {type(statement)}"
    if literal is not None:
        assert statement.token_literal == literal, f"statement token_literal not {literal}. got {statement.token_literal}"

def check_expression(expression: ast.Expression, typ: Any, literal: str = None):
    assert isinstance(expression, typ), f"expression is not a {typ}. got {type(expression)}"
    if literal is not None:
        assert expression.token_literal == literal, f"expression token_literal not {literal}. got {expression.token_literal}"

def test_identifier_expression():
    input = "foobar;"

    l = lexer.Lexer(input)
    p = parser.Parser(l)

    program = p.parse_program()
    check_parser_errors(p)

    check_program_length(program, 1)

    statement = program.statements[0]
    check_statement(statement, ast.ExpressionStatement, "foobar")

    ident = statement.expression
    assert isinstance(ident, ast.Identifier), f"expression is not a Identifier. got {type(ident)}"
    assert ident.value == "foobar", f"ident.value is not foobar. got {ident.value}"
    assert ident.token_literal == "foobar", f"ident.token_literal is not foobar. got {ident.token_literal}"

def test_integer_literal_expression():
    input = "5;"

    l = lexer.Lexer(input)
    p = parser.Parser(l)

    program = p.parse_program()
    check_parser_errors(p)

    check_program_length(program, 1)

    statement = program.statements[0]
    check_statement(statement, ast.ExpressionStatement, "5")
    
    literal = statement.expression
    assert isinstance(literal, ast.IntegerLiteral), f"expression is not an IntegerLiteral. got {type(literal)}"
    assert literal.value == 5, f"literal.value not 5. got {literal.value}"
    assert literal.token_literal == "5", f"literal.token_literal not '5'. got {literal.token_literal}"

def test_boolean_expression():
    input = "true;"

    program = get_program(input, 1)

    statement = program.statements[0]
    check_statement(statement, ast.ExpressionStatement, "true")

    exp = statement.expression
    boolean_literal_test(exp, True)

def get_program(input: str, n_statements: int) -> ast.Program:
    l = lexer.Lexer(input)
    p = parser.Parser(l)
    program = p.parse_program()
    check_parser_errors(p)
    check_program_length(program, n_statements)

    return program

def test_parsing_prefix_expressions():
    prefix_tests = [
        ("!5;", "!", 5),
        ("-15;", "-", 15),
        ("-a;", "-", "a"),
        ("!true", "!", True),
        ("!false", "!", False)
    ]

    for input, operator, value in prefix_tests:
        l = lexer.Lexer(input)
        p = parser.Parser(l)
        program = p.parse_program()
        check_parser_errors(p)
        check_program_length(program, 1)

        statement = program.statements[0]
        check_statement(statement, ast.ExpressionStatement)

        exp = statement.expression

        prefix_expression_test(exp, operator, value)

def value_test(expected: Any, actual: Any):
    assert expected == actual, f"value not {expected}. got {actual}"

def integer_literal_test(exp: ast.IntegerLiteral, value: int):
    check_expression(exp, ast.IntegerLiteral, str(value))
    value_test(value, exp.value)

def identifier_test(exp: ast.Identifier, value: str):
    check_expression(exp, ast.Identifier)
    value_test(value, exp.value)

def boolean_literal_test(exp: ast.Boolean, value: bool):
    check_expression(exp, ast.Boolean)
    value_test(value, exp.value)

def unknow_type(exp, value):
    raise Exception(f"type of expression not handled. got {type(exp)}")

def literal_expression_test(exp: ast.Expression, value: Any):
    type_to_test = {
        int: integer_literal_test,
        str: identifier_test,
        bool: boolean_literal_test
    }
    return type_to_test.get(type(value), unknow_type)(exp, value)

def operator_test(expected: str, actual: str):
    assert actual == expected, f"operator is not {expected}. got {actual}"

def infix_expression_test(exp: ast.Expression, left: Any, operator: str, right: Any):
    check_expression(exp, ast.InfixExpression)

    literal_expression_test(exp.left, left)
    assert exp.operator == operator, f"exp.operator is not {operator}. got {exp.operator}"
    literal_expression_test(exp.right, right)

def prefix_expression_test(exp: ast.Expression, operator: str, right: Any):
    check_expression(exp, ast.PrefixExpression)

    operator_test(operator, exp.operator)
    literal_expression_test(exp.right, right)

def test_parsing_infix_expressions():
    infix_tests = [
        ("5 + 5", 5, "+", 5),
        ("5 - 5", 5, "-", 5),
        ("5*5", 5, "*", 5),
        ("5 / 5", 5, "/", 5),
        ("5 >5", 5, ">", 5),
        ("5< 5", 5, "<", 5),
        ("5 == 5", 5, "==", 5),
        ("5!=5", 5, "!=", 5),
        ("true == true", True, "==", True),
        ("true!=false", True, "!=", False),
    ]

    for input, left_value, operator, right_value in infix_tests:
        l = lexer.Lexer(input)
        p = parser.Parser(l)
        program = p.parse_program()
        check_parser_errors(p)
        check_program_length(program, 1)

        statement = program.statements[0]
        check_statement(statement, ast.ExpressionStatement)

        exp = statement.expression

        infix_expression_test(exp, left_value, operator, right_value)

def test_operator_precedence_parsing():
    tests = [
        [
            "-a * b",
            "((-a)*b)"
        ],
        [
            "!-a",
            "(!(-a))"
        ],
        [
            "a  + b +c",
            "((a+b)+c)"
        ],
        [
            "a + b / c",
            "(a+(b/c))"
        ],
        [
            "a + 3 * c - d / e",
            "((a+(3*c))-(d/e))"
        ],
        [
            "5>4 == 3<4",
            "((5>4)==(3<4))"
        ],
        [
            "true",
            "true"
        ],
        [
            "3 > 5 == false",
            "((3>5)==false)"
        ],
        [
            "true!=false",
            "(true!=false)"
        ],
        [
            "1 + (2 + 3) +4",
            "((1+(2+3))+4)"
        ],
        [
            "!(true == true)",
            "(!(true==true))"
        ]
    ]

    for input, expected in tests:
        l = lexer.Lexer(input)
        p = parser.Parser(l)
        program = p.parse_program()
        check_parser_errors(p)
        check_program_length(program, 1)
        actual = str(program)
        assert actual == expected, f"expected '{expected}', but got '{actual}'"

def test_if_expression():
    input = "if (x<y) { x }"
    program = get_program(input, 1)

    statement = program.statements[0]
    check_statement(statement, ast.ExpressionStatement)

    exp = statement.expression
    check_expression(exp, ast.IfExpression)

    infix_expression_test(exp.condition, "x", "<", "y")
    assert len(exp.consequence.statements) == 1, f"consequence is not 1 statements. got {len(exp.consequence.statements)}"

    consequence = exp.consequence.statements[0]
    check_statement(consequence, ast.ExpressionStatement)

    identifier_test(consequence.expression, "x")

    assert exp.alternative is None, "exp.alternative is not None"

def test_if_else_expression():
    input = "if (x<y) { x } else {y}"
    program = get_program(input, 1)

    statement = program.statements[0]
    check_statement(statement, ast.ExpressionStatement)

    exp = statement.expression
    check_expression(exp, ast.IfExpression)

    infix_expression_test(exp.condition, "x", "<", "y")
    assert len(exp.consequence.statements) == 1, f"consequence is not 1 statements. got {len(exp.consequence.statements)}"

    consequence = exp.consequence.statements[0]
    check_statement(consequence, ast.ExpressionStatement)

    identifier_test(consequence.expression, "x")

    assert exp.alternative is not None, "exp.alternative is None"
    assert len(exp.alternative.statements) == 1, f"alternative is not 1 statements. got {len(exp.alternative.statements)}"

    alternative = exp.alternative.statements[0]
    check_statement(alternative, ast.ExpressionStatement)

    identifier_test(alternative.expression, "y")

def test_function_literal_parsing():
    input = "fn(x, y) { x+y;}"

    program = get_program(input, 1)

    statement = program.statements[0]
    check_statement(statement, ast.ExpressionStatement)

    function = statement.expression
    check_expression(function, ast.FunctionLiteral)

    assert len(function.parameters) == 2, f"function literal parameters number wrong. want 2, got {len(function.parameters)}"

    literal_expression_test(function.parameters[0], "x")
    literal_expression_test(function.parameters[1], "y")

    body_statements = function.body.statements
    assert len(body_statements) == 1, f"function body number of statements is not 1. got {len(body_statements)}"

    body_statement = body_statements[0]
    check_statement(body_statement, ast.ExpressionStatement)

    infix_expression_test(body_statement.expression, "x", "+", "y")

def test_function_parameters_parsing():
    tests = [
        ("fn(){};", []),
        ("fn(x){};", ["x"]),
        ("fn(x, y, z){};", ["x", "y", "z"]),
    ]

    for input, expected_params in tests:
        program = get_program(input, 1)

        statement = program.statements[0]
        function = statement.expression

        assert len(function.parameters) == len(expected_params), f"length of parameters wrong. want {len(expected_params)} but got {len(function.parameters)}"

        for i, param in enumerate(expected_params):
            literal_expression_test(function.parameters[i], param)

def test_call_expression_parsing():
    input = "add(1, 2*3, 4+5);"

    program = get_program(input, 1)

    statement = program.statements[0]
    check_statement(statement, ast.ExpressionStatement)

    exp: ast.CallExpression = statement.expression
    check_expression(exp, ast.CallExpression)

    identifier_test(exp.function, "add")

    assert len(exp.arguments) == 3, f"wrong number of arguments. Expected 3, got {len(exp.arguments)}"

    literal_expression_test(exp.arguments[0], 1)
    infix_expression_test(exp.arguments[1], 2, "*", 3)
    infix_expression_test(exp.arguments[2], 4, "+", 5)

def test_string_literal_expression():
    input = '"Hello world";'
    program = get_program(input, 1)

    statement = program.statements[0]
    check_statement(statement, ast.ExpressionStatement)

    literal = statement.expression
    check_expression(literal, ast.StringLiteral)

    assert literal.value == "Hello world", f"literal.value not 'Hello world'. got {literal.value}"