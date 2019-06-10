from lexer import Lexer
import tokens

def test_next_token():
    input = """let five = 5;
    let ten = 10;
    
    let add = fn(x, y){
        x + y;
    };

    let result = add(five, ten);
    !-/*5;
    5 < 10 > 5;

    if 5 == 10 != 8 {
        return true;
    } else {
        return false;
    }

    # this is a comment it should all be ignored
    #

    not_a_comment; # comments again let return {}

    a_b;
    "foobar"
    "foo bar"
    [1, 2];

    {5: 2};

    for(x in v){};
    """

    tests = [
        (tokens.LET, "let"),
        (tokens.IDENT, "five"),
        (tokens.ASSIGN, "="),
        (tokens.INT, "5"),
        (tokens.SEMICOLON, ";"),

        (tokens.LET, "let"),
        (tokens.IDENT, "ten"),
        (tokens.ASSIGN, "="),
        (tokens.INT, "10"),
        (tokens.SEMICOLON, ";"),

        (tokens.LET, "let"),
        (tokens.IDENT, "add"),
        (tokens.ASSIGN, "="),
        (tokens.FUNCTION, "fn"),
        (tokens.LPAREN, "("),
        (tokens.IDENT, "x"),
        (tokens.COMMA, ","),
        (tokens.IDENT, "y"),
        (tokens.RPAREN, ")"),
        (tokens.LBRACE, "{"),
        (tokens.IDENT, "x"),
        (tokens.PLUS, "+"),
        (tokens.IDENT, "y"),
        (tokens.SEMICOLON, ";"),
        (tokens.RBRACE, "}"),
        (tokens.SEMICOLON, ";"),

        (tokens.LET, "let"),
        (tokens.IDENT, "result"),
        (tokens.ASSIGN, "="),
        (tokens.IDENT, "add"),
        (tokens.LPAREN, "("),
        (tokens.IDENT, "five"),
        (tokens.COMMA, ","),
        (tokens.IDENT, "ten"),
        (tokens.RPAREN, ")"),
        (tokens.SEMICOLON, ";"),

        (tokens.BANG, "!"),
        (tokens.MINUS, "-"),
        (tokens.SLASH, "/"),
        (tokens.ASTERISK, "*"),
        (tokens.INT, "5"),
        (tokens.SEMICOLON, ";"),

        (tokens.INT, "5"),
        (tokens.LT, "<"),
        (tokens.INT, "10"),
        (tokens.GT, ">"),
        (tokens.INT, "5"),
        (tokens.SEMICOLON, ";"),

        (tokens.IF, "if"),
        (tokens.INT, "5"),
        (tokens.EQ, "=="),
        (tokens.INT, "10"),
        (tokens.NOT_EQ, "!="),
        (tokens.INT, "8"),
        (tokens.LBRACE, "{"),
        (tokens.RETURN, "return"),
        (tokens.TRUE, "true"),
        (tokens.SEMICOLON, ";"),
        (tokens.RBRACE, "}"),
        (tokens.ELSE, "else"),
        (tokens.LBRACE, "{"),
        (tokens.RETURN, "return"),
        (tokens.FALSE, "false"),
        (tokens.SEMICOLON, ";"),
        (tokens.RBRACE, "}"),

        (tokens.IDENT, "not_a_comment"),
        (tokens.SEMICOLON, ";"),

        (tokens.IDENT, "a_b"),
        (tokens.SEMICOLON, ";"),

        (tokens.STRING, "foobar"),
        (tokens.STRING, "foo bar"),

        (tokens.LBRACKET, "["),
        (tokens.INT, "1"),
        (tokens.COMMA, ","),
        (tokens.INT, "2"),
        (tokens.RBRACKET, "]"),
        (tokens.SEMICOLON, ";"),

        (tokens.LBRACE, "{"),
        (tokens.INT, "5"),
        (tokens.COLON, ":"),
        (tokens.INT, "2"),
        (tokens.RBRACE, "}"),
        (tokens.SEMICOLON, ";"),

        (tokens.FOR, "for"),
        (tokens.LPAREN, "("),
        (tokens.IDENT, "x"),
        (tokens.IN, "in"),
        (tokens.IDENT, "v"),
        (tokens.RPAREN, ")"),
        (tokens.LBRACE, "{"),
        (tokens.RBRACE, "}"),
        (tokens.SEMICOLON, ";"),

        (tokens.EOF, ""),
    ]

    l = Lexer(input)

    i = 0
    for expected_type, expected_literal in tests:
        tok: tokens.Token = l.next_token()

        assert tok.typ == expected_type, f"Token type wrong: {i}. got {tok.typ}, wanted {expected_type}. token: {tok}"
        assert tok.literal == expected_literal, f"Token literal wrong: {i}"

        i+=1
        