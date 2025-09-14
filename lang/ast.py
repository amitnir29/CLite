from lang.tokens import Token

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class VarDecl(ASTNode):
    def __init__(self, var_name: Token, var_type: Token, init_value: Token):
        self.var_name = var_name
        self.var_type = var_type
        self.init_value = init_value

class FuncDecl(ASTNode):
    def __init__(self, func_name: Token, params: list, body: list):
        self.func_name = func_name
        self.params = params
        self.body = body

class IfStmt(ASTNode):
    def __init__(self, condition: Token, then_branch: ASTNode, else_branch: ASTNode = None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class WhileStmt(ASTNode):
    def __init__(self, condition: Token, body: ASTNode):
        self.condition = condition
        self.body = body

class ForStmt(ASTNode):
    def __init__(self, init: Token, condition: Token, increment: Token, body: ASTNode):
        self.init = init
        self.condition = condition
        self.increment = increment
        self.body = body

class ReturnStmt(ASTNode):
    def __init__(self, value: Token):
        self.value = value

class BreakStmt(ASTNode):
    pass

class ContinueStmt(ASTNode):
    pass

class AssignStmt(ASTNode):
    def __init__(self, var_name: Token, value: Token):
        self.var_name = var_name
        self.value = value

class Expr(ASTNode):
    pass

class BinaryExpr(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryExpr(Expr):
    def __init__(self, operator: Token, operand: Expr):
        self.operator = operator
        self.operand = operand

class Literal(Expr):
    def __init__(self, value: Token):
        self.value = value

class Identifier(Expr):
    def __init__(self, name: Token):
        self.name = name

class CallExpr(Expr):
    def __init__(self, callee: Expr, args: list[Expr]):
        self.callee = callee
        self.args = args
