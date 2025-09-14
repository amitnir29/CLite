import unittest

from lang.lexer import tokenize
from lang.parser import Parser
from lang.ast import AssignStmt, BinaryExpr, UnaryExpr, Identifier, Literal, CallExpr


class TestParserExpressions(unittest.TestCase):
    def parse_code(self, code):
        tokens = tokenize(code)
        parser = Parser(tokens)
        return parser.parse()

    def test_precedence_add_mul(self):
        ast = self.parse_code("x = 1 + 2 * 3;")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, AssignStmt)
        expr = stmt.value
        # x = 1 + (2 * 3)
        self.assertIsInstance(expr, BinaryExpr)
        self.assertEqual(expr.operator.value, '+')
        self.assertIsInstance(expr.left, Literal)
        self.assertEqual(expr.left.value.value, '1')
        self.assertIsInstance(expr.right, BinaryExpr)
        self.assertEqual(expr.right.operator.value, '*')

    def test_parenthesized_changes_precedence(self):
        ast = self.parse_code("x = (1 + 2) * 3;")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, AssignStmt)
        expr = stmt.value
        # x = (1 + 2) * 3
        self.assertIsInstance(expr, BinaryExpr)
        self.assertEqual(expr.operator.value, '*')
        self.assertIsInstance(expr.left, BinaryExpr)
        self.assertEqual(expr.left.operator.value, '+')

    def test_unary_minus(self):
        ast = self.parse_code("x = -1;")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, AssignStmt)
        self.assertIsInstance(stmt.value, UnaryExpr)
        self.assertEqual(stmt.value.operator.value, '-')

    def test_logical_and_equality(self):
        ast = self.parse_code("x = 1 == 1 && 2 < 3;")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, AssignStmt)
        top = stmt.value
        self.assertIsInstance(top, BinaryExpr)
        self.assertEqual(top.operator.value, '&&')
        self.assertIsInstance(top.left, BinaryExpr)
        self.assertEqual(top.left.operator.value, '==')
        self.assertIsInstance(top.right, BinaryExpr)
        self.assertEqual(top.right.operator.value, '<')

    def test_call_expression(self):
        ast = self.parse_code("x = add(40, 2);")
        stmt = ast.statements[0]
        self.assertIsInstance(stmt, AssignStmt)
        call = stmt.value
        self.assertIsInstance(call, CallExpr)
        self.assertIsInstance(call.callee, Identifier)
        self.assertEqual(call.callee.name.value, 'add')
        self.assertEqual(len(call.args), 2)


if __name__ == "__main__":
    unittest.main()

