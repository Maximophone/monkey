import click

import repl
from monkey_object import Environment, NULL
import monkey_object as mobject
from lexer import Lexer
from parser import Parser
import evaluator

@click.command()
@click.argument("file", required=False)
@click.option("-i", "--interactive", is_flag=True)
@click.option("-d", "--debug", is_flag=True)
def main(file, interactive=False, debug=False):
    if file is not None:
        env = Environment()

        with open(file, "r") as f:
            program_str = f.read()

        l = Lexer(program_str)
        p = Parser(l)

        program = p.parse_program()

        if debug:
            print("PARSED PROGRAM")
            print("-"*50)
            print(program)
            print("-"*50)

        if len(p.errors) != 0:
            repl.print_parser_errors(p.errors)
            exit(0)

        evaluated = evaluator.eval(program, env)
        if (not interactive and evaluated is not None and evaluated != NULL) or evaluated.typ == mobject.ERROR_OBJ:
            print(evaluated.inspect)
        if interactive:
            repl.start(env=env)
    else:
        repl.start()


if __name__ == "__main__":
    main()