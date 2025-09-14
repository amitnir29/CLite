import unittest
from lang.lexer import tokenize
from lang.parser import Parser
from lang.ast import Program, VarDecl, AssignStmt, Identifier, Literal, FuncDecl, IfStmt, WhileStmt, ReturnStmt

class TestParser(unittest.TestCase):
    def parse_code(self, code):
        tokens = tokenize(code)
        parser = Parser(tokens)
        return parser.parse()

    def test_var_decl(self):
        code = "let x: int = 42;"
        ast = self.parse_code(code)
        self.assertIsInstance(ast, Program)
        self.assertIsInstance(ast.statements[0], VarDecl)
        self.assertEqual(ast.statements[0].var_name.value, "x")
        self.assertEqual(ast.statements[0].var_type.value, "int")
        self.assertEqual(ast.statements[0].init_value.value.value, "42")

    def test_assignment(self):
        code = "x = 5;"
        ast = self.parse_code(code)
        self.assertIsInstance(ast.statements[0], AssignStmt)
        self.assertEqual(ast.statements[0].var_name.value, "x")
        self.assertEqual(ast.statements[0].value.value, "5")

    def test_func_decl(self):
        code = "fn main(): int { let x: int = 1; return x; }"
        ast = self.parse_code(code)
        self.assertIsInstance(ast.statements[0], FuncDecl)
        self.assertEqual(ast.statements[0].func_name.value, "main")
        self.assertEqual(ast.statements[0].body[0].var_name.value, "x")
        self.assertIsInstance(ast.statements[0].body[1], ReturnStmt)

    def test_if_stmt(self):
        code = "if (x) { x = 1; } else { x = 2; }"
        ast = self.parse_code(code)
        self.assertIsInstance(ast.statements[0], IfStmt)
        self.assertIsInstance(ast.statements[0].then_branch, list)
        self.assertIsInstance(ast.statements[0].else_branch, list)

    def test_while_stmt(self):
        code = "while (x) { x = x; }"
        ast = self.parse_code(code)
        self.assertIsInstance(ast.statements[0], WhileStmt)
        self.assertIsInstance(ast.statements[0].body, list)

    def test_return_stmt(self):
        code = "return 42;"
        ast = self.parse_code(code)
        self.assertIsInstance(ast.statements[0], ReturnStmt)
        self.assertEqual(ast.statements[0].value.value, "42")

if __name__ == "__main__":
    unittest.main()
