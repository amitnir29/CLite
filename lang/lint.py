from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set

from lang.lexer import tokenize
from lang.parser import Parser
from lang.tokens import Token, TokenType, KEYWORDS
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
    Expr,
    BinaryExpr,
    UnaryExpr,
    Literal,
    Identifier,
    CallExpr,
)


@dataclass(frozen=True)
class LintWarning:
    code: str
    message: str
    line: int
    column: int


def lint_code(code: str) -> List[LintWarning]:
    tokens = tokenize(code)
    warnings: List[LintWarning] = []
    warnings.extend(_lint_missing_semicolons(tokens))
    warnings.extend(_lint_missing_colon_in_let(tokens))
    warnings.extend(_lint_unbalanced_delimiters(tokens))
    warnings.extend(_lint_control_missing_paren(tokens))

    # Run parser to get AST for semantic checks. If it fails, we still return semicolon warnings.
    try:
        program = Parser(tokens).parse()
    except Exception:
        return warnings

    warnings.extend(_lint_undefined_variables(program))
    return warnings


def _lint_missing_semicolons(tokens: List[Token]) -> List[LintWarning]:
    # Heuristic scan: certain statements must end with ';' at brace depth 0 and outside parentheses
    req_end_keywords = {"let", "return", "break", "continue"}
    stmt_start_keywords = {"let", "fn", "if", "while", "for", "return", "break", "continue", "else"}

    def needs_end_start(tok: Token) -> bool:
        if tok.type == TokenType.KEYWORD and tok.value in req_end_keywords:
            return True
        if tok.type in (TokenType.IDENT, TokenType.INT, TokenType.FLOAT, TokenType.STRING):
            return True  # expression/assignment statements
        if tok.type == TokenType.LPAREN:
            return True
        return False

    def is_boundary(tok: Token) -> bool:
        # Reached a point where a new statement is likely to start
        if tok.type in (TokenType.RBRACE, TokenType.LBRACE):
            return True
        if tok.type in (TokenType.IDENT, TokenType.INT, TokenType.FLOAT, TokenType.STRING, TokenType.LPAREN):
            return True
        if tok.type == TokenType.KEYWORD and tok.value in stmt_start_keywords:
            return True
        return False

    out: List[LintWarning] = []
    n = len(tokens)
    i = 0
    brace_depth = 0
    paren_depth = 0

    suppress_until_lbrace_level = None  # used to skip function header tokens until '{'
    while i < n:
        t = tokens[i]
        if t.type == TokenType.LBRACE:
            brace_depth += 1
            # If we were suppressing header tokens, clear when we hit the body open
            if suppress_until_lbrace_level is not None and brace_depth > suppress_until_lbrace_level:
                suppress_until_lbrace_level = None
            i += 1
            continue
        if t.type == TokenType.RBRACE:
            brace_depth = max(0, brace_depth - 1)
            i += 1
            continue
        if t.type == TokenType.LPAREN:
            paren_depth += 1
        elif t.type == TokenType.RPAREN:
            paren_depth = max(0, paren_depth - 1)

        # Detect 'fn' header to suppress checks until its body '{'
        if paren_depth == 0 and t.type == TokenType.KEYWORD and t.value == 'fn' and suppress_until_lbrace_level is None:
            suppress_until_lbrace_level = brace_depth
            i += 1
            continue

        # Only consider statement starts at top paren level and not in suppressed header
        if paren_depth == 0 and suppress_until_lbrace_level is None and needs_end_start(t):
            start_brace = brace_depth
            j = i + 1
            inner_paren = paren_depth
            found_end = False
            last_type = t.type
            while j < n:
                tj = tokens[j]
                if tj.type == TokenType.LPAREN:
                    inner_paren += 1
                elif tj.type == TokenType.RPAREN:
                    inner_paren = max(0, inner_paren - 1)

                if inner_paren == 0 and brace_depth == start_brace and tj.type == TokenType.END:
                    found_end = True
                    j += 1  # move past ';' for next scan
                    break
                # Boundary: start of a new statement after a call/primary, e.g., `print(x) x = 1;`
                if (
                    inner_paren == 0
                    and brace_depth == start_brace
                    and (
                        tj.type == TokenType.RBRACE
                        or (tj.type == TokenType.KEYWORD and tj.value in stmt_start_keywords)
                        or (tj.type == TokenType.IDENT and last_type == TokenType.RPAREN)
                    )
                ):
                    break
                # track last significant token type
                last_type = tj.type
                j += 1

            if not found_end:
                out.append(LintWarning(
                    code="W001",
                    message="Possible missing ';' at end of statement",
                    line=t.line,
                    column=t.column,
                ))
                # Jump to boundary to avoid duplicate warnings for same statement
                i = max(i + 1, j)
                continue
            else:
                # Semicolon present; continue scanning from just after it
                i = j
                continue
        i += 1
    return out


def _lint_undefined_variables(program: Program) -> List[LintWarning]:
    out: List[LintWarning] = []
    builtins: Set[str] = {"print"}

    scopes: list[Set[str]] = [set(builtins)]

    def define(name: str):
        scopes[-1].add(name)

    def is_defined(name: str) -> bool:
        return any(name in s for s in reversed(scopes))

    # Hoist function names to global
    for st in program.statements:
        if isinstance(st, FuncDecl):
            define(st.func_name.value)

    def visit_block(stmts: list):
        scopes.append(set())
        for s in stmts:
            visit_stmt(s)
        scopes.pop()

    def visit_stmt(node):
        if isinstance(node, VarDecl):
            # init may reference variables
            visit_expr(node.init_value)
            define(node.var_name.value)
            return

        if isinstance(node, AssignStmt):
            if not is_defined(node.var_name.value):
                out.append(LintWarning(
                    code="W002",
                    message=f"Assignment to undefined variable '{node.var_name.value}'",
                    line=node.var_name.line,
                    column=node.var_name.column,
                ))
            visit_expr(node.value)
            return

        if isinstance(node, IfStmt):
            visit_expr(node.condition)
            if isinstance(node.then_branch, list):
                visit_block(node.then_branch)
            else:
                visit_stmt(node.then_branch)
            if node.else_branch is not None:
                if isinstance(node.else_branch, list):
                    visit_block(node.else_branch)
                else:
                    visit_stmt(node.else_branch)
            return

        if isinstance(node, WhileStmt):
            visit_expr(node.condition)
            if isinstance(node.body, list):
                visit_block(node.body)
            else:
                visit_stmt(node.body)
            return

        if isinstance(node, ForStmt):
            scopes.append(set())
            visit_stmt(node.init)
            visit_expr(node.condition)
            visit_stmt(node.increment)
            if isinstance(node.body, list):
                visit_block(node.body)
            else:
                visit_stmt(node.body)
            scopes.pop()
            return

        if isinstance(node, ReturnStmt):
            visit_expr(node.value)
            return

        if isinstance(node, (BreakStmt, ContinueStmt)):
            return

        if isinstance(node, Expr):
            visit_expr(node)
            return

        if isinstance(node, list):
            visit_block(node)
            return

    def visit_expr(node):
        if isinstance(node, Token):
            return
        if isinstance(node, Literal):
            return
        if isinstance(node, Identifier):
            name_tok = node.name
            if not is_defined(name_tok.value):
                out.append(LintWarning(
                    code="W002",
                    message=f"Use of undefined variable '{name_tok.value}'",
                    line=name_tok.line,
                    column=name_tok.column,
                ))
            return
        if isinstance(node, UnaryExpr):
            visit_expr(node.operand)
            return
        if isinstance(node, BinaryExpr):
            visit_expr(node.left)
            visit_expr(node.right)
            return
        if isinstance(node, CallExpr):
            visit_expr(node.callee)
            for a in node.args:
                visit_expr(a)
            return

    for st in program.statements:
        visit_stmt(st)

    return out


def _lint_missing_colon_in_let(tokens: List[Token]) -> List[LintWarning]:
    out: List[LintWarning] = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        if t.type == TokenType.KEYWORD and t.value == 'let':
            if i + 1 < n and tokens[i + 1].type == TokenType.IDENT:
                # Expect COLON after identifier
                if i + 2 < n and tokens[i + 2].type != TokenType.COLON:
                    name_tok = tokens[i + 1]
                    out.append(LintWarning(
                        code='W003',
                        message="Missing ':' in variable declaration",
                        line=name_tok.line,
                        column=name_tok.column,
                    ))
        i += 1
    return out


def _lint_unbalanced_delimiters(tokens: List[Token]) -> List[LintWarning]:
    out: List[LintWarning] = []
    stack: list[tuple[str, Token]] = []  # (kind, token)
    pairs = {')': '(', '}': '{', ']': '['}
    for t in tokens:
        if t.type in (TokenType.LPAREN, TokenType.LBRACE, TokenType.LBRACKET):
            kind = '(' if t.type == TokenType.LPAREN else '{' if t.type == TokenType.LBRACE else '['
            stack.append((kind, t))
        elif t.type in (TokenType.RPAREN, TokenType.RBRACE, TokenType.RBRACKET):
            kind = ')' if t.type == TokenType.RPAREN else '}' if t.type == TokenType.RBRACE else ']'
            if not stack or stack[-1][0] != pairs[kind]:
                out.append(LintWarning(
                    code='W004',
                    message=f"Unmatched '{kind}'",
                    line=t.line,
                    column=t.column,
                ))
            else:
                stack.pop()
    # Anything left is unclosed
    for kind, tok in stack:
        out.append(LintWarning(
            code='W004',
            message=f"Unclosed '{kind}'",
            line=tok.line,
            column=tok.column,
        ))
    return out


def _lint_control_missing_paren(tokens: List[Token]) -> List[LintWarning]:
    out: List[LintWarning] = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        if t.type == TokenType.KEYWORD and t.value in ('if', 'while', 'for'):
            # Expect '(' immediately next (ignoring nothing, since we are token-based)
            if i + 1 >= n or tokens[i + 1].type != TokenType.LPAREN:
                out.append(LintWarning(
                    code='W005',
                    message=f"Expected '(' after '{t.value}'",
                    line=t.line,
                    column=t.column,
                ))
        i += 1
    return out


__all__ = ["LintWarning", "lint_code"]
