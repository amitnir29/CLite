import unittest
from lang import lexer
from lang.tokens import Token, TokenType

class TestParserTokenize(unittest.TestCase):
    def test_simple_assignment(self):
        code = "x = 42;"
        expected = [
            Token(type=TokenType.IDENT, value='x', line=1, column=1),
            Token(type=TokenType.ASSIGN, value='=', line=1, column=3),
            Token(type=TokenType.INT, value='42', line=1, column=5),
            Token(type=TokenType.END, value=';', line=1, column=7)
        ]
        self.assertEqual(lexer.tokenize(code), expected)

    def test_arithmetic_expression(self):
        code = "result = a + b * 2;"
        expected = [
            Token(type=TokenType.IDENT, value='result', line=1, column=1),
            Token(type=TokenType.ASSIGN, value='=', line=1, column=8),
            Token(type=TokenType.IDENT, value='a', line=1, column=10),
            Token(type=TokenType.OP, value='+', line=1, column=12),
            Token(type=TokenType.IDENT, value='b', line=1, column=14),
            Token(type=TokenType.OP, value='*', line=1, column=16),
            Token(type=TokenType.INT, value='2', line=1, column=18),
            Token(type=TokenType.END, value=';', line=1, column=19)
        ]
        self.assertEqual(lexer.tokenize(code), expected)

    def test_parentheses_and_braces(self):
        code = "y = (x + 1) * 3;"
        expected = [
            Token(type=TokenType.IDENT, value='y', line=1, column=1),
            Token(type=TokenType.ASSIGN, value='=', line=1, column=3),
            Token(type=TokenType.LPAREN, value='(', line=1, column=5),
            Token(type=TokenType.IDENT, value='x', line=1, column=6),
            Token(type=TokenType.OP, value='+', line=1, column=8),
            Token(type=TokenType.INT, value='1', line=1, column=10),
            Token(type=TokenType.RPAREN, value=')', line=1, column=11),
            Token(type=TokenType.OP, value='*', line=1, column=13),
            Token(type=TokenType.INT, value='3', line=1, column=15),
            Token(type=TokenType.END, value=';', line=1, column=16)
        ]
        self.assertEqual(lexer.tokenize(code), expected)

    def test_braces(self):
        code = "{ x = 1; y = 2; }"
        expected = [
            Token(type=TokenType.LBRACE, value='{', line=1, column=1),
            Token(type=TokenType.IDENT, value='x', line=1, column=3),
            Token(type=TokenType.ASSIGN, value='=', line=1, column=5),
            Token(type=TokenType.INT, value='1', line=1, column=7),
            Token(type=TokenType.END, value=';', line=1, column=8),
            Token(type=TokenType.IDENT, value='y', line=1, column=10),
            Token(type=TokenType.ASSIGN, value='=', line=1, column=12),
            Token(type=TokenType.INT, value='2', line=1, column=14),
            Token(type=TokenType.END, value=';', line=1, column=15),
            Token(type=TokenType.RBRACE, value='}', line=1, column=17)
        ]
        self.assertEqual(lexer.tokenize(code), expected)

    def test_float_number(self):
        code = "pi = 3.14;"
        expected = [
            Token(type=TokenType.IDENT, value='pi', line=1, column=1),
            Token(type=TokenType.ASSIGN, value='=', line=1, column=4),
            Token(type=TokenType.FLOAT, value='3.14', line=1, column=6),
            Token(type=TokenType.END, value=';', line=1, column=10)
        ]
        self.assertEqual(lexer.tokenize(code), expected)

    def test_unexpected_character(self):
        code = "x = 5$;"
        with self.assertRaises(SyntaxError):
            lexer.tokenize(code)

if __name__ == "__main__":
    unittest.main()
