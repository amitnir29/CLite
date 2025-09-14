import re
from typing import List, Tuple
from lang.tokens import Token

# Define token specifications: (token_name, regex_pattern)
TOKEN_SPECIFICATION = [
    ('NUMBER',   r'\d+(\.\d*)?'),      # Integer or decimal number
    ('ID',       r'[A-Za-z_]\w*'),     # Identifiers
    ('ASSIGN',   r'='),                # Assignment operator
    ('END',      r';'),                # Statement terminator
    ('OP',       r'[+\-*/]'),          # Arithmetic operators
    ('LPAREN',   r'\('),               # Left Parenthesis
    ('RPAREN',   r'\)'),               # Right Parenthesis
    ('LBRACE',   r'\{'),               # Left Brace
    ('RBRACE',   r'\}'),               # Right Brace
    ('SKIP',     r'[ \t]+'),           # Skip over spaces and tabs
    ('NEWLINE',  r'\n'),               # Line endings
    ('MISMATCH', r'.'),                # Any other character
]

# Compile regex
token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATION)
get_token = re.compile(token_regex).match

def tokenize(code: str) -> List[Token]:
    tokens = []
    pos = 0
    line = 1
    line_start = 0
    code_len = len(code)
    while pos < code_len:
        match = get_token(code, pos)
        if not match:
            if code[pos] in ('\n', ' ', '\t'):
                pos += 1
                continue
            raise SyntaxError(f'Unexpected character: {code[pos]}')
        kind = match.lastgroup
        value = match.group()
        if kind == 'NEWLINE':
            line += 1
            line_start = match.end()
        elif kind == 'SKIP':
            pass
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected token: {value}')
        else:
            column = match.start() - line_start + 1
            tokens.append(Token(kind, value, line, column))
        pos = match.end()
    return tokens

# Example usage:
if __name__ == "__main__":
    code = "x = 42 + 3.14;"
    for token in tokenize(code):
        print(token)