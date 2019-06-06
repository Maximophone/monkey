import monkey_ast as ast
import tokens

def test_string():
    program = ast.Program(
        statements=[
            ast.LetStatement(
                token=tokens.Token(typ=tokens.LET, literal="let"),
                name=ast.Identifier(
                    token=tokens.Token(typ=tokens.IDENT, literal="my_var"),
                    value="my_var"
                ),
                value=ast.Identifier(
                    token=tokens.Token(typ=tokens.IDENT, literal="another_var"),
                    value="another_var"
                )
            )
        ]
    )

    expected = "let my_var = another_var;"
    assert str(program) == expected, f"str(program) wrong. got '{str(program)}'' but expected '{expected}'"