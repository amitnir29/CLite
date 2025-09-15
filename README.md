# Clite — a tiny C-like language (for learning & fun)

## Project Goals

- Learn about compilers more
- Have fun
- End up with a tiny language I can actually run


## Language Syntax (quick guide)

### Comments
    // single line
    /* block comment */

### Types (v0)
- `int`, `bool`, `void`  
*(Optional later: `string`, arrays `T[]`, `struct`)*

### Declarations & Assignment
    let x: int = 1;
    x = x + 41;

### Literals
    42
    true
    false
    "hello" (hopefully)

### Operators (high → low precedence)
- Unary: `!`, `-`
- Multiplicative: `*`, `/`, `%`
- Additive: `+`, `-`
- Relational: `<`, `<=`, `>`, `>=`
- Equality: `==`, `!=`
- Logical: `&&`, `||` (short-circuit)
- Assignment: `=`

### Control Flow
    if (cond) { ... } else { ... }
    while (cond) { ... }
    return expr;     // inside functions

### Functions
    fn add(a: int, b: int): int {
        return a + b;
    }

    fn main(): void {
        let y: int = add(40, 2);
        print(y);    // (builtins?)
    }

### Tiny Example
    // hello.cl
    fn main(): void {
        let x: int = 40 + 2;
        print(x);
    }

---

## Goal Checklist (tick as I go)

### MVP — make programs run
- [ ] **Lexer**: identifiers, ints, operators, comments
- [ ] **Parser**: expressions, `;` statements, blocks `{ }`, functions
- [ ] **AST**: nodes for Program/Func/Block/If/While/BinOp/Call
- [ ] **Types**: `int`, `bool`, `void`
- [ ] **Type checker**: variables, returns, function calls
- [ ] **Runtime**: simple bytecode + stack-based VM
- [ ] **Builtin**: `print`
- [ ] **Examples**: `hello`, `fib`, a small loop demo
- [ ] **Nice errors**: file:line:col with a caret under the code

### Core language v1
- [ ] Variables: `let` + assignment, block scoping & shadowing
- [ ] Control flow: `if/else`, `while`, short-circuit `&&`/`||`
- [ ] Operators: `+ - * / %`, comparisons, equality, unary `!`/`-`
- [ ] Functions: typed params/returns, call/return stack
- [ ] Return rules: require return in non-void paths

### Quality of life
- [ ] `fmt`: formatter for indentation & spaces
- [ ] `check`: type-check without running
- [ ] REPL: quick lex/parse/type/execute loop
- [ ] Tests: unit (lexer/parser/types) + end-to-end (run programs)

### Optional
- [ ] **Strings** (immutable) and `"..."` literals
- [ ] **Arrays** `T[]` with bounds checks in debug mode
- [ ] **Structs**: `struct Point { x:int; y:int; }` and `p.x`
- [ ] **Optimizations**: constant folding, dead code elimination
- [ ] **Garbage collector** (mark-sweep) for heap objects

## Running code

- CLI usage via module:
  - Run a file and call `main`:
    - `python -m lang.cli examples/hello.cl`
  - Specify entrypoint function:
    - `python -m lang.cli path/to/file.cl --entry start`
  - Run top-level only (no function call):
    - `python -m lang.cli path/to/file.cl --no-entry`

- Makefile helpers:
  - Run an example: `make run EX=examples/hello.cl`
  - Run all tests: `make test`
  - Run common examples: `make examples`

## Examples

Each example includes a Run line at the top; a few quick ones:

- Hello world:
  - `python -m lang.cli examples/hello.cl`
- Function call returning a value (42):
  - `python -m lang.cli examples/add.cl`
- While loop decrementing to zero:
  - `python -m lang.cli examples/loop.cl`
- Control flow with booleans and short-circuit:
  - `python -m lang.cli examples/controls.cl`

## Tests

- Run the full suite:
  - `make test`
  - or individually:
    - `python -m unittest tests/lexer_test.py -v`
    - `python -m unittest tests/parser_test.py -v`
    - `python -m unittest tests/parser_expr_test.py -v`
    - `python -m unittest tests/interpreter_test.py -v`
