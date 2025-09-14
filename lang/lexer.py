import re
from typing import List
from lang.tokens import Token, TokenType, OPERATORS, KEYWORDS

# Build a regex for operators and punctuation, preferring longest match first
_OP_LITERALS = sorted(OPERATORS, key=len, reverse=True)
_OP_REGEX = "|".join(re.escape(op) for op in _OP_LITERALS)

# Master regex with named groups; order matters for priority
_MASTER_REGEX = re.compile(
    "|".join(
        [
            r"(?P<NEWLINE>\n)",
            r"(?P<SKIP>[ \t\r]+)",
            r"(?P<LINE_COMMENT>//[^\n]*)",
            r"(?P<BLOCK_COMMENT>/\*.*?\*/)",
            r"(?P<STRING>\"([^\\\n\"]|\\.)*\")",
            r"(?P<FLOAT>\d+\.\d+)",
            r"(?P<INT>\d+)",
            r"(?P<IDENT>[A-Za-z_]\w*)",
            rf"(?P<OP>{_OP_REGEX})",
        ]
    ),
    flags=re.DOTALL,
)


def tokenize(code: str) -> List[Token]:
    tokens: List[Token] = []
    pos = 0
    line = 1
    line_start = 0
    code_len = len(code)

    while pos < code_len:
        m = _MASTER_REGEX.match(code, pos)
        if not m:
            # Unknown character
            ch = code[pos]
            if ch in ("\n", " ", "\t", "\r"):
                pos += 1
                continue
            raise SyntaxError(f"Unexpected character: {ch}")

        kind = m.lastgroup
        lexeme = m.group()

        if kind == "NEWLINE":
            line += 1
            line_start = m.end()
            pos = m.end()
            continue
        if kind in ("SKIP", "LINE_COMMENT", "BLOCK_COMMENT"):
            pos = m.end()
            continue

        column = m.start() - line_start + 1

        if kind == "INT":
            tokens.append(Token(TokenType.INT, lexeme, line, column))
        elif kind == "FLOAT":
            tokens.append(Token(TokenType.FLOAT, lexeme, line, column))
        elif kind == "STRING":
            tokens.append(Token(TokenType.STRING, lexeme, line, column))
        elif kind == "IDENT":
            if lexeme in KEYWORDS:
                tokens.append(Token(TokenType.KEYWORD, lexeme, line, column))
            else:
                tokens.append(Token(TokenType.IDENT, lexeme, line, column))
        elif kind == "OP":
            # Map punctuation/operators into specific TokenTypes when needed
            if lexeme == "=":
                tokens.append(Token(TokenType.ASSIGN, lexeme, line, column))
            elif lexeme == ";":
                tokens.append(Token(TokenType.END, lexeme, line, column))
            elif lexeme == "(":
                tokens.append(Token(TokenType.LPAREN, lexeme, line, column))
            elif lexeme == ")":
                tokens.append(Token(TokenType.RPAREN, lexeme, line, column))
            elif lexeme == "{":
                tokens.append(Token(TokenType.LBRACE, lexeme, line, column))
            elif lexeme == "}":
                tokens.append(Token(TokenType.RBRACE, lexeme, line, column))
            elif lexeme == "[":
                tokens.append(Token(TokenType.LBRACKET, lexeme, line, column))
            elif lexeme == "]":
                tokens.append(Token(TokenType.RBRACKET, lexeme, line, column))
            elif lexeme == ",":
                tokens.append(Token(TokenType.COMMA, lexeme, line, column))
            elif lexeme == ".":
                tokens.append(Token(TokenType.DOT, lexeme, line, column))
            elif lexeme == ":":
                tokens.append(Token(TokenType.COLON, lexeme, line, column))
            else:
                tokens.append(Token(TokenType.OP, lexeme, line, column))
        else:
            # Should not reach here due to exhaustive groups
            raise SyntaxError(f"Unexpected token: {lexeme}")

        pos = m.end()

    return tokens

if __name__ == "__main__":
    sample = "fn main(): int { let x: int = 1; while (x) { x = x; } return x; }"
    for t in tokenize(sample):
        print(t)
