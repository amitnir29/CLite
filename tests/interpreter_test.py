import unittest

from lang.interpreter import run


class TestInterpreter(unittest.TestCase):
    def test_arithmetic(self):
        code = 'fn main(): int { return 1 + 2 * 3; }'
        self.assertEqual(run(code, entrypoint='main'), 7)

    def test_if_bool(self):
        code = 'fn main(): int { if (true) { return 2; } else { return 3; } }'
        self.assertEqual(run(code, entrypoint='main'), 2)

    def test_while_loop(self):
        code = 'fn main(): int { let x: int = 3; while (x) { x = x - 1; } return x; }'
        self.assertEqual(run(code, entrypoint='main'), 0)

    def test_function_call(self):
        code = 'fn add(a: int, b: int): int { return a + b; } fn main(): int { return add(40, 2); }'
        self.assertEqual(run(code, entrypoint='main'), 42)

    def test_unary_ops(self):
        code = 'fn main(): int { let x: int = 1; x = -x; if (!false) { return x + 41; } return 0; }'
        self.assertEqual(run(code, entrypoint='main'), 40)


if __name__ == "__main__":
    unittest.main()

