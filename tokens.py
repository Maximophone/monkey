from dataclasses import dataclass

class TokenType(str):
    pass

@dataclass
class Token:
    typ: TokenType = None
    literal: str = None

# Token Types

ILLEGAL = "ILLEGAL"
EOF = "EOF"

IDENT = "IDENT"
INT = "INT"
STRING = "STRING"

ASSIGN = "="
PLUS = "+"
MINUS = "-"
BANG = "!"
ASTERISK = "*"
SLASH = "/"
LT = "<"
GT = ">"

EQ = "=="
NOT_EQ = "!="

COMMA = ","
SEMICOLON = ";"
COLON = ":"

LPAREN = "("
RPAREN = ")"
LBRACE = "{"
RBRACE = "}"
LBRACKET = "["
RBRACKET = "]"

FUNCTION = "FUNCTION"
LET = "LET"
TRUE = "TRUE"
FALSE = "FALSE"
IF = "IF"
ELSE = "ELSE"
RETURN = "RETURN"
FOR = "FOR"
IN = "IN"


token_ch_dict = {
    "=": Token(ASSIGN, "="),
    ";": Token(SEMICOLON, ";"),
    ":": Token(COLON, ":"),
    "(": Token(LPAREN, "("),
    ")": Token(RPAREN, ")"),
    ",": Token(COMMA, ","),
    "+": Token(PLUS, "+"),
    "{": Token(LBRACE, "{"),
    "}": Token(RBRACE, "}"),
    "!": Token(BANG, "!"),
    "-": Token(MINUS, "-"),
    "*": Token(ASTERISK, "*"),
    "/": Token(SLASH, "/"),
    "<": Token(LT, "<"),
    ">": Token(GT, ">"),
    "[": Token(LBRACKET, "["),
    "]": Token(RBRACKET, "]"),
    0: Token(EOF, ""),
}

token_ch2_dict = {
    "==": Token(EQ, "=="),
    "!=": Token(NOT_EQ, "!="),
}

token_alpha_dict = {
    "let": Token(LET, "let"),
    "fn": Token(FUNCTION, "fn"),
    "true": Token(TRUE, "true"),
    "false": Token(FALSE, "false"),
    "if": Token(IF, "if"),
    "else": Token(ELSE, "else"),
    "return": Token(RETURN, "return"),
    "for": Token(FOR, "for"),
    "in": Token(IN, "in"),
}

peeking = {
    "=",
    "!",
}