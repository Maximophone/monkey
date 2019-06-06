import tokens
import lexer
import monkey_ast as ast
from typing import List

class Parser:
    def __init__(self, lexer: lexer.Lexer):
        self.lexer: lexer.Lexer = lexer
        self.errors: List[str] = []

        self.cur_token: tokens.Token = None
        self.peek_token: tokens.Token = None

        self.next_token()
        self.next_token()

    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def parse_program(self):
        program = ast.Program()
        while self.cur_token.typ != tokens.EOF:
            statement = self.parse_statement()
            if statement is not None:
                program.statements.append(statement)
            self.next_token()
        return program
    
    def parse_statement(self):
        parse_typ_dict = {
            tokens.LET: self.parse_let_statement,
            tokens.RETURN: self.parse_return_statement,
        }
        return parse_typ_dict.get(self.cur_token.typ, lambda: None)()

    def parse_let_statement(self):
        statement = ast.LetStatement(token=self.cur_token)

        if not self.expect_peek(tokens.IDENT):
            return None

        statement.name = ast.Identifier(token=self.cur_token, value=self.cur_token.literal)

        if not self.expect_peek(tokens.ASSIGN):
            return None

        while not self.cur_token_is(tokens.SEMICOLON):
            self.next_token()

        return statement

    def parse_return_statement(self):
        statement = ast.ReturnStatement(token=self.cur_token)

        self.next_token()

        while not self.cur_token_is(tokens.SEMICOLON):
            self.next_token()

        return statement

    def cur_token_is(self, t: tokens.TokenType) -> bool:
        return self.cur_token.typ == t

    def peek_token_is(self, t: tokens.TokenType) -> bool:
        return self.peek_token.typ == t

    def expect_peek(self, t: tokens.TokenType) -> bool:
        if self.peek_token_is(t):
            self.next_token()
            return True
        else:
            self.peek_error(t)
            return False

    def peek_error(self, t: tokens.TokenType):
        message = f"expected next token to be {t}, got {self.peek_token.typ} instead"
        self.errors.append(message)

