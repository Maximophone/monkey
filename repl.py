import lexer
import parser
import tokens
import evaluator
import monkey_object as mobject

from typing import List
import readline

PROMPT = ">>"

def start(env=None):
    if env is None:
        env = mobject.Environment()
    while True:
        print(PROMPT, end=" ")
        line = input()
        if not line:
            return
        
        l = lexer.Lexer(line)
        p = parser.Parser(l)

        program = p.parse_program()
        if len(p.errors) != 0:
            print_parser_errors(p.errors)
            continue

        evaluated = evaluator.eval(program, env)
        if evaluated is not None:
            print(evaluated.inspect)


def print_parser_errors(errors: List[str]):
    print("Woops! Parser Errors!")
    for error in errors:
        print(f"    {error}")