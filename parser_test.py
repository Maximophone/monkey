import lexer
import monkey_ast as ast
import parser


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
