"""
Token definitions for clite.
Lexer lives in a separate module; this file only defines token types,
the Token dataclass, and language keyword/operator sets.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Set, List

class TokenType(Enum):
    # structural
    IDENT = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()

    # operators / punctuation
    OP = auto()

    # others
    KEYWORD = auto()
    EOF = auto()

@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    line: int = 0
    column: int = 0

    def __str__(self):
        return f"Token(type={self.type}, value='{self.value}', line={self.line}, column={self.column})"

# Basic keywords of the language (extend as needed)
KEYWORDS: Set[str] = {
    "if", "else", "while", "for", "return",
    "break", "continue", "struct", "typedef",
    "var", "const", "func", "true", "false", "null",
}

# Operators and punctuation (kept here for reference / reuse by the lexer)
OPERATORS: List[str] = [
    "==", "!=", "<=", ">=", "&&", "||", "++", "--",
    "+=", "-=", "*=", "/=", "%=", "->", "<<", ">>",
    "+", "-", "*", "/", "%", "<", ">", "=", "!", "&", "|", "^", "~",
    "(", ")", "{", "}", "[", "]", ";", ",", ".", ":", "?"
]

__all__ = ["TokenType", "Token", "KEYWORDS", "OPERATORS"]
