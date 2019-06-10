import click

import repl
from monkey_object import Environment, NULL
from lexer import Lexer
from parser import Parser
import evaluator

@click.command()
@click.argument("file", required=False)
@click.option("-i", "--interactive", is_flag=True)
def main(file, interactive=False):
    if file is not None:
        env = Environment()

        with open(file, "r") as f:
            program_str = f.read()

        l = Lexer(program_str)
        p = Parser(l)

        program = p.parse_program()

        if len(p.errors) != 0:
            repl.print_parser_errors(p.errors)
            exit(0)

        evaluated = evaluator.eval(program, env)
        if not interactive and evaluated is not None and evaluated != NULL:
            print(evaluated.inspect)
        if interactive:
            repl.start(env=env)
    else:
        repl.start()


if __name__ == "__main__":
    main()