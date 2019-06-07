import lexer
import monkey_ast as ast
import parser
from typing import Any


def test_let_statements():
    input = """
    let x = 5;
    let y = 10;
    let foobar = 019837;
    """

    l = lexer.Lexer(input)
    p = parser.Parser(l)

    program = p.parse_program()
    check_parser_errors(p)

    assert program is not None, f"parse_program() returned  None"
    assert len(program.statements) == 3, f"program.statements does not contain 3 statements. got {len(program.statements)}"

    tests = [
        ("x",),
        ("y",),
        ("foobar",),
    ]

    for i, (expected_identifier, ) in enumerate(tests):
        statement = program.statements[i]
        let_statement_test(statement, expected_identifier)


def test_return_statements():
    input = """
    return 5;
    return 10;
    return add(15);
    """

    l = lexer.Lexer(input)
    p = parser.Parser(l)

    program = p.parse_program()
    check_parser_errors(p)

    assert program is not None, f"parser_program() returned None"
    assert len(program.statements) == 3, f"program.statements does not contain 3 statements, got {len(program.statements)}"

    for statement in program.statements:
        assert statement.token_literal == "return", f"statement token_literal not 'return'. got {statement.token_literal}"
        assert isinstance(statement, ast.ReturnStatement), f"statement is not a ReturnStatement. got {type(statement)}"


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

def test_parsing_prefix_expressions():
    prefix_tests = [
        ("!5;", "!", 5),
        ("-15;", "-", 15)
    ]

    for input, operator, integer_value in prefix_tests:
        l = lexer.Lexer(input)
        p = parser.Parser(l)
        program = p.parse_program()
        check_parser_errors(p)
        check_program_length(program, 1)

        statement = program.statements[0]
        check_statement(statement, ast.ExpressionStatement)

        exp = statement.expression
        check_expression(exp, ast.PrefixExpression)

        assert exp.operator == operator, f"operator is not {operator}. got {exp.operator}"
        integer_literal_test(exp.right, integer_value)

def integer_literal_test(exp: ast.IntegerLiteral, value: int):
    check_expression(exp, ast.IntegerLiteral, str(value))
    assert exp.value == value, f"value not {value}. got {exp.value}"

def test_parsing_infix_expressions():
    infix_tests = [
        ("5 + 5", 5, "+", 5),
        ("5 - 5", 5, "-", 5),
        ("5*5", 5, "*", 5),
        ("5 / 5", 5, "/", 5),
        ("5 >5", 5, ">", 5),
        ("5< 5", 5, "<", 5),
        ("5 == 5", 5, "==", 5),
        ("5!=5", 5, "!=", 5)
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
        check_expression(exp, ast.InfixExpression)

        integer_literal_test(exp.left, left_value)
        assert exp.operator == operator, f"operator is not {operator}. got {exp.operator}"
        integer_literal_test(exp.right, right_value)

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