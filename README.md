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
- [x] **Lexer**: identifiers, ints/floats, strings, operators, comments
- [x] **Parser**: expressions, `;` statements, blocks `{ }`, functions
- [x] **AST**: nodes for Program/Func/If/While/Return/Assign/BinOp/Unary/Call
- [x] **Types (syntax)**: `int`, `bool`, `void`
- [ ] **Type checker**: variables, returns, function calls
- [x] **Runtime**: AST interpreter
- [x] **Builtin**: `print`
- [x] **Examples**: `hello`, `loop`, `controls`
- [ ] **Nice errors**: file:line:col with a caret under the code

### Core language v1
- [x] Variables: `let` + assignment, block scoping
- [x] Control flow: `if/else`, `while`, short-circuit `&&`/`||`
- [x] Operators: `+ - * / %`, comparisons, equality, unary `!`/`-`
- [x] Functions: typed params/returns, call/return
- [ ] Return rules: require return in non-void paths

### Quality of life
- [ ] `fmt`: formatter for indentation & spaces
- [ ] `check`: type-check without running
- [ ] REPL: quick lex/parse/type/execute loop
- [x] Tests: unit (lexer/parser/interpreter)
- [x] Linter: basic static checks (W001–W006)
- [x] CLI: `python -m lang.cli` and Makefile helpers

### Optional
- [x] **Strings**: `"..."` literals (basic)
- [ ] **Arrays** `T[]`
- [ ] **Structs**: `struct Point { x:int; y:int; }` and `p.x`
- [ ] **Optimizations**: constant folding, dead code elimination
- [ ] **Garbage collector** (mark-sweep)

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

## Linting

Static checks for common issues (missing `;`, undefined variables):

- Lint a file:
  - `python -m lang.lint_cli examples/hello.cl`
- Fail on warnings (CI):
  - `python -m lang.lint_cli --fail-on-warn examples/*.cl`
- Makefile helper:
  - `make lint EX=examples/hello.cl`

Warnings emitted
- W001: Possible missing ';' at end of statement
- W002: Use/assignment of undefined variable
- W003: Missing ':' in variable declaration (`let x: T = ...`)
- W004: Unbalanced delimiters (unmatched/uncclosed () {} [])
- W005: Expected '(' after control keyword (`if`/`while`/`for`)
- W006: Unclosed string literal

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
