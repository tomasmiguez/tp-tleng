import sys

from regex import RegEx
from .errors import SyntaxError
from .lexer import lexer
from .parser import parser

__all__ = ["parse_regex", "SyntaxError"]


def parse_regex(regex_str: str) -> RegEx:
    lexer.input(regex_str)

    return parser.parse(lexer=lexer)
