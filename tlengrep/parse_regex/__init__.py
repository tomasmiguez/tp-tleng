import sys

from regex import RegEx
from .errors import SyntaxError
from .lexer import lexer
from .parser import parser

__all__ = ["parse_regex", "SyntaxError"]


def parse_regex(regex_str: str) -> RegEx:
    lexer.input(regex_str)
    try:
        return parser.parse(lexer=lexer)
    except SyntaxError as e:
        raise SyntaxError(e.message, e.lineno, e.lexpos)
    # NO IMPLEMENTAR este método para la primera entrega del TP.
    # Forma parte de la segunda entrega.
    raise NotImplementedError
