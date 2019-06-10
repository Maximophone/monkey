# Monkey

Python implementation of the Monkey Programming language, according to book "Writing an Interpreter in Go".

Example of program:

```
# This is a comment.
let hello = "Hello "; # basic types are be integers, booleans or strings
let b = 3 + 5*2;

# functions are first order objects
let my_function = fn(c){
    if(b<c){
        return "World";
    };
};

puts(hello + my_function(100)) # Prints "Hello World" to the console
```

To run a program

```bash
./monkey <my_program.mky>
```

To run the repl
```bash
./monkey
```

To run a program in interactive mode:
```bash
./monkey -i <my_program.mky>
```