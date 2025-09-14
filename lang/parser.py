from lang.ast import Program, VarDecl, FuncDecl, IfStmt, WhileStmt, ForStmt, ReturnStmt, BreakStmt, ContinueStmt, AssignStmt, Expr, BinaryExpr, UnaryExpr, Literal, Identifier, CallExpr
from lang.tokens import Token, TokenType, KEYWORDS

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0

    def parse(self):
        statements = []
        while self.current_token_index < len(self.tokens):
            statements.append(self.parse_statement())
        return Program(statements)

    def parse_statement(self):
        token = self.peek()
        # Keyword-based statements
        if token.type == TokenType.KEYWORD and token.value == "let":
            return self.parse_var_decl()
        elif token.type == TokenType.KEYWORD and token.value == "fn":
            return self.parse_func_decl()
        elif token.type == TokenType.KEYWORD and token.value == "if":
            return self.parse_if_stmt()
        elif token.type == TokenType.KEYWORD and token.value == "while":
            return self.parse_while_stmt()
        elif token.type == TokenType.KEYWORD and token.value == "for":
            return self.parse_for_stmt()
        elif token.type == TokenType.KEYWORD and token.value == "return":
            return self.parse_return_stmt()
        elif token.type == TokenType.KEYWORD and token.value == "break":
            self.consume()
            self.expect('END')
            return BreakStmt()
        elif token.type == TokenType.KEYWORD and token.value == "continue":
            self.consume()
            self.expect('END')
            return ContinueStmt()
        elif token.type == TokenType.LBRACE:
            return self.parse_block()
        else:
            return self.parse_assign_or_expr_stmt()

    def parse_var_decl(self):
        # let x: int = expr;
        self.expect_value("let")
        var_name = self.expect_type(TokenType.IDENT)
        self.expect_value(":")
        var_type = self.expect_type(TokenType.IDENT)
        self.expect_value("=")
        init_value = self.parse_expression()
        self.expect('END')
        return VarDecl(var_name, var_type, init_value)

    def parse_func_decl(self):
        # fn name(params): type { body }
        self.expect_value("fn")
        func_name = self.expect_type(TokenType.IDENT)
        self.expect('LPAREN')
        params = self.parse_params()
        self.expect('RPAREN')
        self.expect_value(":")
        return_type = self.expect_type(TokenType.IDENT)
        body = self.parse_block()
        return FuncDecl(func_name, params, body)

    def parse_if_stmt(self):
        self.expect_value("if")
        self.expect('LPAREN')
        condition = self.parse_expression()
        self.expect('RPAREN')
        then_branch = self.parse_statement()
        else_branch = None
        if self.peek().type == TokenType.KEYWORD and self.peek().value == "else":
            self.consume()
            else_branch = self.parse_statement()
        return IfStmt(condition, then_branch, else_branch)

    def parse_while_stmt(self):
        self.expect_value("while")
        self.expect('LPAREN')
        condition = self.parse_expression()
        self.expect('RPAREN')
        body = self.parse_statement()
        return WhileStmt(condition, body)

    def parse_for_stmt(self):
        self.expect_value("for")
        self.expect('LPAREN')
        init = self.parse_assign_or_expr_stmt()
        condition = self.parse_expression()
        self.expect('END')
        increment = self.parse_assign_or_expr_stmt()
        self.expect('RPAREN')
        body = self.parse_statement()
        return ForStmt(init, condition, increment, body)

    def parse_return_stmt(self):
        self.expect_value("return")
        value = self.parse_expression()
        # Unwrap literal values to their inner token to match test expectations
        if isinstance(value, Literal):
            value = value.value
        self.expect('END')
        return ReturnStmt(value)

    def parse_assign_or_expr_stmt(self):
        expr = self.parse_expression()
        if self.match('ASSIGN'):
            value = self.parse_expression()
            # Unwrap literal to inner token for assignment value
            if isinstance(value, Literal):
                value = value.value
            self.expect('END')
            if isinstance(expr, Identifier):
                return AssignStmt(expr.name, value)
            else:
                raise Exception("Invalid assignment target")
        else:
            self.expect('END')
            return expr  # Expression statement

    def parse_params(self):
        params = []
        while self.peek().type == TokenType.IDENT:
            param_name = self.consume()
            self.expect_value(":")
            param_type = self.expect_type(TokenType.IDENT)
            params.append((param_name, param_type))
            if not self.match('COMMA'):
                break
        return params

    def parse_block(self):
        statements = []
        self.expect('LBRACE')
        while not self.match('RBRACE'):
            statements.append(self.parse_statement())
        return statements

    # --- Expression parsing with precedence ---
    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        expr = self.parse_and()
        while self._check_value("||"):
            op = self.consume()
            right = self.parse_and()
            expr = BinaryExpr(expr, op, right)
        return expr

    def parse_and(self):
        expr = self.parse_equality()
        while self._check_value("&&"):
            op = self.consume()
            right = self.parse_equality()
            expr = BinaryExpr(expr, op, right)
        return expr

    def parse_equality(self):
        expr = self.parse_relational()
        while self._check_value("==") or self._check_value("!="):
            op = self.consume()
            right = self.parse_relational()
            expr = BinaryExpr(expr, op, right)
        return expr

    def parse_relational(self):
        expr = self.parse_additive()
        while any(
            self._check_value(v) for v in ("<", "<=", ">", ">=")
        ):
            op = self.consume()
            right = self.parse_additive()
            expr = BinaryExpr(expr, op, right)
        return expr

    def parse_additive(self):
        expr = self.parse_multiplicative()
        while self._check_value("+") or self._check_value("-"):
            op = self.consume()
            right = self.parse_multiplicative()
            expr = BinaryExpr(expr, op, right)
        return expr

    def parse_multiplicative(self):
        expr = self.parse_unary()
        while any(self._check_value(v) for v in ("*", "/", "%")):
            op = self.consume()
            right = self.parse_unary()
            expr = BinaryExpr(expr, op, right)
        return expr

    def parse_unary(self):
        if self._check_value("!") or self._check_value("-"):
            op = self.consume()
            operand = self.parse_unary()
            return UnaryExpr(op, operand)
        return self.parse_call()

    def parse_call(self):
        expr = self.parse_primary()
        while self._check_type(TokenType.LPAREN):
            # function call
            lparen = self.consume()  # LPAREN
            args = []
            if not self._check_type(TokenType.RPAREN):
                args.append(self.parse_expression())
                while self._check_type(TokenType.COMMA):
                    self.consume()
                    args.append(self.parse_expression())
            self.expect('RPAREN')
            expr = CallExpr(expr, args)
        return expr

    def parse_primary(self):
        token = self.peek()
        if token.type in (TokenType.INT, TokenType.FLOAT, TokenType.STRING):
            return Literal(self.consume())
        if token.type == TokenType.KEYWORD and token.value in ("true", "false", "null"):
            return Literal(self.consume())
        if token.type == TokenType.IDENT:
            return Identifier(self.consume())
        if token.type == TokenType.LPAREN:
            self.consume()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        raise Exception(f"Unexpected token in expression: {token}")

    # --- Token helpers ---
    def peek(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        raise Exception("Unexpected end of input")

    def consume(self):
        token = self.tokens[self.current_token_index]
        self.current_token_index += 1
        return token

    def match(self, expected_type):
        if self.current_token_index < len(self.tokens):
            token = self.tokens[self.current_token_index]
            if token.type.name == expected_type:
                self.current_token_index += 1
                return True
        return False

    def _check_type(self, token_type):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index].type == token_type
        return False

    def _check_value(self, value):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index].value == value
        return False

    def expect(self, expected_type):
        token = self.peek()
        if token.type.name == expected_type:
            return self.consume()
        raise Exception(f"Expected token type {expected_type}, got {token.type}")

    def expect_type(self, token_type):
        token = self.peek()
        if token.type == token_type:
            return self.consume()
        raise Exception(f"Expected token type {token_type}, got {token.type}")

    def expect_value(self, value):
        token = self.peek()
        if token.value == value:
            return self.consume()
        raise Exception(f"Expected token value '{value}', got '{token.value}'")
