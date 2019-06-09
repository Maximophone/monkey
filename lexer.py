import tokens
from tokens import Token

class Lexer:
    def __init__(self, input):
        self.input: str = input
        self.position: int = 0
        self.read_position: int = 0
        self.ch: str

        self.read_char()

    def read_char(self):
        if self.read_position >= len(self.input):
            self.ch = 0
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def read_identifier(self):
        position = self.position
        while self.ch!=0 and is_alpha(self.ch):
            self.read_char()
        return self.input[position:self.position]

    def read_number(self):
        position = self.position
        while self.ch!=0 and self.ch.isdigit():
            self.read_char()
        return self.input[position:self.position]

    def peek_char(self):
        if self.read_position >= len(self.input):
            return 0
        else:
            return self.input[self.read_position]


    def next_token(self):

        while self.ch!=0 and self.ch.isspace():
            self.read_char()

        if self.ch!=0 and is_alpha(self.ch):
            literal = self.read_identifier()
            tok = tokens.token_alpha_dict.get(literal, Token(tokens.IDENT, literal))
        elif self.ch!=0 and self.ch.isdigit():
            literal = self.read_number()
            tok = Token(tokens.INT, literal)
        else:
            if self.ch in tokens.peeking:
                next_ch = self.peek_char()
                tok = tokens.token_ch2_dict.get(self.ch+str(next_ch))
                if tok is not None:
                    self.read_char()
                    self.read_char()
                    return tok
            tok = tokens.token_ch_dict.get(self.ch, Token(tokens.ILLEGAL, self.ch))
            self.read_char()
        return tok

def is_alpha(char: str) -> bool:
    return char.isalpha() or char=="_"