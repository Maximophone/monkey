import tokens
import lexer
import monkey_ast as ast
from typing import List, Dict, Callable


LOWEST = 1
EQUALS = 2
LESSGREATER = 3
SUM = 4
PRODUCT = 5
PREFIX = 6
CALL = 7
INDEX = 8

precedences = {
    tokens.EQ: EQUALS,
    tokens.NOT_EQ: EQUALS,
    tokens.LT: LESSGREATER,
    tokens.GT: LESSGREATER,
    tokens.PLUS: SUM,
    tokens.MINUS: SUM,
    tokens.SLASH: PRODUCT,
    tokens.ASTERISK: PRODUCT,
    tokens.LPAREN: CALL,
    tokens.LBRACKET: INDEX
}

class Parser:
    def __init__(self, lexer: lexer.Lexer):
        self.lexer: lexer.Lexer = lexer
        self.errors: List[str] = []

        self.cur_token: tokens.Token = None
        self.peek_token: tokens.Token = None

        self.prefix_parse_functions: Dict[tokens.TokenType, Callable] = {
            tokens.IDENT: self.parse_identifier,
            tokens.INT: self.parse_integer_literal,
            tokens.STRING: self.parse_string_literal,
            tokens.TRUE: self.parse_boolean,
            tokens.FALSE: self.parse_boolean,
            tokens.BANG: self.parse_prefix_expression,
            tokens.MINUS: self.parse_prefix_expression,
            tokens.LPAREN: self.parse_grouped_expression,
            tokens.IF: self.parse_if_expression,
            tokens.FUNCTION: self.parse_function_literal,
            tokens.LBRACKET: self.parse_array_literal,
            tokens.LBRACE: self.parse_hash_literal,
            tokens.FOR: self.parse_for_expression,
        }
        self.infix_parse_functions: Dict[tokens.TokenType, Callable] = {
            tokens.PLUS: self.parse_infix_expression,
            tokens.MINUS: self.parse_infix_expression,
            tokens.SLASH: self.parse_infix_expression,
            tokens.ASTERISK: self.parse_infix_expression,
            tokens.EQ: self.parse_infix_expression,
            tokens.NOT_EQ: self.parse_infix_expression,
            tokens.LT: self.parse_infix_expression,
            tokens.GT: self.parse_infix_expression,
            tokens.LPAREN: self.parse_call_expression,
            tokens.LBRACKET: self.parse_index_expression,
        }

        self.next_token()
        self.next_token()

    def register_prefix(self, token_type: tokens.TokenType, prefix_parse_function: Callable):
        self.prefix_parse_functions[token_type] = prefix_parse_function
    
    def register_infix(self, token_type: tokens.TokenType, infix_parse_function: Callable):
        self.infix_parse_functions[token_type] = infix_parse_function

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
        return parse_typ_dict.get(self.cur_token.typ, self.parse_expression_statement)()

    def parse_let_statement(self):
        statement = ast.LetStatement(token=self.cur_token)

        if not self.expect_peek(tokens.IDENT):
            return None

        statement.name = ast.Identifier(token=self.cur_token, value=self.cur_token.literal)

        if not self.expect_peek(tokens.ASSIGN):
            return None

        self.next_token()
        statement.value = self.parse_expression(LOWEST)

        if self.peek_token_is(tokens.SEMICOLON):
            self.next_token()

        return statement

    def parse_return_statement(self):
        statement = ast.ReturnStatement(token=self.cur_token)

        self.next_token()

        statement.return_value = self.parse_expression(LOWEST)

        if self.peek_token_is(tokens.SEMICOLON):
            self.next_token()

        return statement

    def parse_expression_statement(self):
        statement = ast.ExpressionStatement(token=self.cur_token)
        statement.expression = self.parse_expression(LOWEST)
        if self.peek_token_is(tokens.SEMICOLON):
            self.next_token()
        return statement

    def parse_expression(self, precedence: int):
        prefix = self.prefix_parse_functions.get(self.cur_token.typ)
        if prefix is None:
            self.no_prefix_parse_function(self.cur_token.typ)
            return None
        left_exp = prefix()
        while not self.peek_token_is(tokens.SEMICOLON) and precedence < self.peek_precedence():
            infix = self.infix_parse_functions.get(self.peek_token.typ)
            if infix is None:
                return left_exp
            self.next_token()
            left_exp = infix(left_exp)
        return left_exp

    def no_prefix_parse_function(self, t: tokens.TokenType):
        self.errors.append(f"no prefix parse function for {t} found")

    def parse_identifier(self) -> ast.Expression:
        return ast.Identifier(token=self.cur_token, value=self.cur_token.literal)

    def parse_integer_literal(self) -> ast.Expression:
        lit = ast.IntegerLiteral(token=self.cur_token)
        try:
            value = int(self.cur_token.literal)
        except BaseException as e:
            self.errors.append(str(e))
            return None
        lit.value = value
        return lit

    def parse_boolean(self) -> ast.Expression:
        return ast.Boolean(
            token=self.cur_token,
            value=self.cur_token_is(tokens.TRUE)
        )

    def parse_string_literal(self) -> ast.Expression:
        return ast.StringLiteral(
            token=self.cur_token,
            value=self.cur_token.literal
        )

    def parse_array_literal(self) -> ast.Expression:
        array = ast.ArrayLiteral(token=self.cur_token)
        array.elements = self.parse_expression_list(tokens.RBRACKET)
        return array
    
    def parse_hash_literal(self) -> ast.Expression:
        hash = ast.HashLiteral(token=self.cur_token)
        hash.pairs = []

        while not self.peek_token_is(tokens.RBRACE):
            self.next_token()
            key = self.parse_expression(LOWEST)

            if not self.expect_peek(tokens.COLON):
                return None

            self.next_token()

            value = self.parse_expression(LOWEST)

            hash.pairs.append((key, value))
            
            if not self.peek_token_is(tokens.RBRACE) and not self.expect_peek(tokens.COMMA):
                return None

        if not self.expect_peek(tokens.RBRACE):
            return None

        return hash


    def parse_if_expression(self) -> ast.Expression:
        exp = ast.IfExpression(token=self.cur_token)

        if not self.expect_peek(tokens.LPAREN):
            return None
        
        self.next_token()
        exp.condition = self.parse_expression(LOWEST)

        if not self.expect_peek(tokens.RPAREN):
            return None

        if not self.expect_peek(tokens.LBRACE):
            return None

        exp.consequence = self.parse_block_statement()

        if self.peek_token_is(tokens.ELSE):
            self.next_token()

            if not self.expect_peek(tokens.LBRACE):
                return None

            exp.alternative = self.parse_block_statement()

        return exp

    def parse_for_expression(self) -> ast.Expression:

        if not self.expect_peek(tokens.LPAREN):
            return None

        self.next_token()

        ident = ast.Identifier(token=self.cur_token, value=self.cur_token.literal)

        if not self.expect_peek(tokens.IN):
            return None

        self.next_token()

        iterator = self.parse_expression(LOWEST)

        if not self.expect_peek(tokens.RPAREN):
            return None

        if not self.expect_peek(tokens.LBRACE):
            return None

        body = self.parse_block_statement()

        return ast.ForExpression(
            token=self.cur_token,
            iterator=iterator,
            element=ident,
            body=body
        )

    def parse_block_statement(self) -> ast.BlockStatement:
        block = ast.BlockStatement(
            token=self.cur_token, 
            statements=[])

        self.next_token()

        while not self.cur_token_is(tokens.RBRACE):
            statement = self.parse_statement()
            if statement is not None:
                block.statements.append(statement)
            self.next_token()
        return block

    def parse_function_literal(self) -> ast.Expression:
        lit = ast.FunctionLiteral(token=self.cur_token)

        if not self.expect_peek(tokens.LPAREN):
            return None
        
        lit.parameters = self.parse_function_parameters()

        if not self.expect_peek(tokens.LBRACE):
            return None

        lit.body = self.parse_block_statement()

        return lit

    def parse_function_parameters(self) -> List[ast.Identifier]:
        identifiers: List[ast.Identifier] = []

        if self.peek_token_is(tokens.RPAREN):
            self.next_token()
            return identifiers

        self.next_token()

        ident: ast.Identifier = ast.Identifier(token = self.cur_token, value= self.cur_token.literal)
        identifiers.append(ident)

        while self.peek_token_is(tokens.COMMA):
            self.next_token()
            self.next_token()
            ident = ast.Identifier(
                token=self.cur_token,
                value=self.cur_token.literal
            )
            identifiers.append(ident)

        if not self.expect_peek(tokens.RPAREN):
            return None
        
        return identifiers

    def parse_call_expression(self, function: ast.Expression) -> ast.Expression:
        exp = ast.CallExpression(
            token=self.cur_token,
            function=function
        )
        exp.arguments = self.parse_expression_list(tokens.RPAREN)
        return exp

    def parse_index_expression(self, left: ast.Expression) -> ast.Expression:
        exp = ast.IndexExpression(
            token = self.cur_token,
            left = left
        )
        self.next_token()
        exp.index = self.parse_expression(LOWEST)
        if not self.expect_peek(tokens.RBRACKET):
            return None
        return exp

    def parse_expression_list(self, end: tokens.TokenType) -> List[ast.Expression]:
        args: List[ast.Expression] = []

        if self.peek_token_is(end):
            self.next_token()
            return args

        self.next_token()
        args.append(self.parse_expression(LOWEST))

        while self.peek_token_is(tokens.COMMA):
            self.next_token()
            self.next_token()
            args.append(self.parse_expression(LOWEST))

        if not self.expect_peek(end):
            return None

        return args

    def parse_prefix_expression(self) -> ast.Expression:
        expression = ast.PrefixExpression(
            token=self.cur_token,
            operator=self.cur_token.literal
        )
        self.next_token()
        expression.right = self.parse_expression(PREFIX)
        return expression

    def parse_infix_expression(self, left: ast.Expression) -> ast.Expression:
        expression = ast.InfixExpression(
            token=self.cur_token,
            operator=self.cur_token.literal,
            left=left
        )
        precedence = self.cur_precedence()
        self.next_token()
        expression.right = self.parse_expression(precedence)
        return expression

    def parse_grouped_expression(self) -> ast.Expression:
        self.next_token()

        exp = self.parse_expression(LOWEST)

        if not self.expect_peek(tokens.RPAREN):
            return None
        
        return exp

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

    def cur_precedence(self) -> int:
        return precedences.get(self.cur_token.typ, LOWEST)

    def peek_precedence(self) -> int:
        return precedences.get(self.peek_token.typ, LOWEST)