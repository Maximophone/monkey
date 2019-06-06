from lexer import Lexer
import tokens

PROMPT = ">>"

def start():
    while True:
        print(PROMPT)
        line = input()
        if not line:
            return
        
        l = Lexer(line)
        
        tok = l.next_token()
        while tok.typ != tokens.EOF:
            print(tok)
            tok = l.next_token()