from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from lang.lexer import tokenize
from lang.parser import Parser
from lang.ast import (
    Program,
    VarDecl,
    FuncDecl,
    IfStmt,
    WhileStmt,
    ForStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    AssignStmt,
    Literal,
    Identifier,
    Expr,
    BinaryExpr,
    UnaryExpr,
    CallExpr,
)
from lang.tokens import Token, TokenType


class ReturnSignal(Exception):
    def __init__(self, value: Any):
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


@dataclass
class Function:
    name: str
    params: List[Tuple[Token, Token]]  # (name, type)
    body: List[Any]  # list of statements (AST nodes)
    closure: "Env"  # captured environment at declaration

    def call(self, interp: "Interpreter", args: List[Any]) -> Any:
        if len(args) != len(self.params):
            raise RuntimeError(f"Function {self.name} expected {len(self.params)} args, got {len(args)}")
        local = Env(parent=self.closure)
        for (p_name, _p_type), arg in zip(self.params, args):
            local.set(p_name.value, arg)
        try:
            interp.exec_block(self.body, local)
        except ReturnSignal as rs:
            return rs.value
        return None


class Env:
    def __init__(self, parent: Optional["Env"] = None):
        self.parent = parent
        self.values: Dict[str, Any] = {}

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise NameError(f"Undefined variable '{name}'")

    def set(self, name: str, value: Any) -> None:
        # Assign in nearest scope that already has the variable, else define in current.
        if name in self.values:
            self.values[name] = value
            return
        if self.parent is not None:
            try:
                self.parent.assign(name, value)
                return
            except NameError:
                pass
        # Define if not existing anywhere
        self.values[name] = value

    def assign(self, name: str, value: Any) -> None:
        if name in self.values:
            self.values[name] = value
        elif self.parent is not None:
            self.parent.assign(name, value)
        else:
            raise NameError(f"Undefined variable '{name}'")


class Interpreter:
    def __init__(self):
        self.globals = Env()
        self.functions: Dict[str, Function] = {}

        # Builtins (minimal)
        def _print(*vals):
            print(*vals)

        self.globals.set("print", _print)

    # --- Public API ---
    def run_code(self, code: str, entrypoint: Optional[str] = None) -> Any:
        tokens = tokenize(code)
        program = Parser(tokens).parse()
        return self.run(program, entrypoint=entrypoint)

    def run(self, program: Program, entrypoint: Optional[str] = None) -> Any:
        # First pass: hoist/collect function declarations
        for stmt in program.statements:
            if isinstance(stmt, FuncDecl):
                fn = Function(
                    name=stmt.func_name.value,
                    params=stmt.params,
                    body=stmt.body,
                    closure=self.globals,
                )
                self.functions[fn.name] = fn
                self.globals.set(fn.name, fn)

        # Execute top-level statements (non-function declarations)
        for stmt in program.statements:
            if not isinstance(stmt, FuncDecl):
                self.exec_stmt(stmt, self.globals)

        # If requested, invoke an entrypoint function
        if entrypoint is not None and entrypoint in self.functions:
            return self.functions[entrypoint].call(self, [])
        return None

    # --- Execution helpers ---
    def exec_block(self, statements: List[Any], env: Env) -> None:
        # Blocks introduce a new scope
        block_env = Env(parent=env)
        for st in statements:
            self.exec_stmt(st, block_env)

    def exec_stmt(self, node: Any, env: Env) -> Any:
        if isinstance(node, VarDecl):
            name = node.var_name.value
            value = self.eval_expr(node.init_value, env)
            env.set(name, value)
            return None

        if isinstance(node, AssignStmt):
            name = node.var_name.value
            value = self.eval_expr(node.value, env)
            env.assign(name, value)
            return None

        if isinstance(node, IfStmt):
            cond = self.truthy(self.eval_expr(node.condition, env))
            if cond:
                # then_branch may be a list (block) or a single statement
                if isinstance(node.then_branch, list):
                    self.exec_block(node.then_branch, env)
                else:
                    self.exec_stmt(node.then_branch, env)
            else:
                if node.else_branch is not None:
                    if isinstance(node.else_branch, list):
                        self.exec_block(node.else_branch, env)
                    else:
                        self.exec_stmt(node.else_branch, env)
            return None

        if isinstance(node, WhileStmt):
            while self.truthy(self.eval_expr(node.condition, env)):
                try:
                    if isinstance(node.body, list):
                        self.exec_block(node.body, env)
                    else:
                        self.exec_stmt(node.body, env)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
            return None

        if isinstance(node, ForStmt):
            # Basic for: init; while (condition) { body; increment; }
            self.exec_stmt(node.init, env)
            while self.truthy(self.eval_expr(node.condition, env)):
                try:
                    if isinstance(node.body, list):
                        self.exec_block(node.body, env)
                    else:
                        self.exec_stmt(node.body, env)
                except ContinueSignal:
                    pass
                except BreakSignal:
                    break
                finally:
                    self.exec_stmt(node.increment, env)
            return None

        if isinstance(node, ReturnStmt):
            val = self.eval_expr(node.value, env)
            raise ReturnSignal(val)

        if isinstance(node, BreakStmt):
            raise BreakSignal()

        if isinstance(node, ContinueStmt):
            raise ContinueSignal()

        if isinstance(node, Expr):
            # Expression statement; evaluate and discard
            _ = self.eval_expr(node, env)
            return None

        if isinstance(node, list):
            # Treat raw block list as a block
            self.exec_block(node, env)
            return None

        raise RuntimeError(f"Unsupported statement node: {type(node).__name__}")

    def eval_expr(self, node: Any, env: Env) -> Any:
        # Certain places store raw Tokens instead of Expr nodes
        if isinstance(node, Token):
            return self.literal_from_token(node)

        if isinstance(node, Literal):
            return self.literal_from_token(node.value)

        if isinstance(node, Identifier):
            return env.get(node.name.value)

        if isinstance(node, UnaryExpr):
            op = node.operator.value
            val = self.eval_expr(node.operand, env)
            if op == '!':
                return not self.truthy(val)
            if op == '-':
                return -val
            raise RuntimeError(f"Unsupported unary operator: {op}")

        if isinstance(node, BinaryExpr):
            op = node.operator.value
            # Short-circuit for logical ops
            if op == '&&':
                left = self.eval_expr(node.left, env)
                if not self.truthy(left):
                    return False
                right = self.eval_expr(node.right, env)
                return self.truthy(right)
            if op == '||':
                left = self.eval_expr(node.left, env)
                if self.truthy(left):
                    return True
                right = self.eval_expr(node.right, env)
                return self.truthy(right)

            left = self.eval_expr(node.left, env)
            right = self.eval_expr(node.right, env)
            if op == '+':
                return left + right
            if op == '-':
                return left - right
            if op == '*':
                return left * right
            if op == '/':
                return left / right
            if op == '%':
                return left % right
            if op == '<':
                return left < right
            if op == '<=':
                return left <= right
            if op == '>':
                return left > right
            if op == '>=':
                return left >= right
            if op == '==':
                return left == right
            if op == '!=':
                return left != right
            raise RuntimeError(f"Unsupported binary operator: {op}")

        if isinstance(node, CallExpr):
            callee_val = self.eval_expr(node.callee, env)
            args = [self.eval_expr(a, env) for a in node.args]
            if isinstance(callee_val, Function):
                return callee_val.call(self, args)
            if callable(callee_val):
                return callee_val(*args)
            raise RuntimeError("Attempted to call a non-callable value")

        # Future: more expression kinds
        raise RuntimeError(f"Unsupported expression node: {type(node).__name__}")

    # --- Utils ---
    def literal_from_token(self, tok: Token) -> Any:
        if tok.type == TokenType.INT:
            return int(tok.value)
        if tok.type == TokenType.FLOAT:
            return float(tok.value)
        if tok.type == TokenType.STRING:
            return self._unquote(tok.value)
        if tok.type == TokenType.KEYWORD:
            if tok.value == 'true':
                return True
            if tok.value == 'false':
                return False
            if tok.value == 'null':
                return None
        # For identifiers used as literals (shouldn't happen), return raw value
        return tok.value

    def _unquote(self, s: str) -> str:
        # Remove surrounding quotes and unescape common sequences
        if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
            s = s[1:-1]
        return bytes(s, "utf-8").decode("unicode_escape")

    def truthy(self, v: Any) -> bool:
        return bool(v)


def run(code: str, entrypoint: Optional[str] = None) -> Any:
    return Interpreter().run_code(code, entrypoint=entrypoint)


__all__ = ["Interpreter", "run", "Env", "Function"]
