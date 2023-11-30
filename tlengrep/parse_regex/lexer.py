import re
from typing import Self
import ply.lex as lex
from ply.lex import TOKEN

class RegexRange:
    def __init__(self, min: int, max: int) -> None:
        self.min = min
        self.max = max

    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, RegexRange):
            return False

        return self.min == other.min and self.max == other.max

tokens = (
    'CHAR',
    'ESCAPED',
    'RANGE',
    'CLASS',
)

literals = "|*+?()[]"

escaped = r'\\(.)'
@TOKEN(escaped)
def t_ESCAPED(t):
    t.value = t.lexer.lexmatch.group(2)
    return t

def t_RANGE(t):
    r'\{(?:(?P<min>\d+),)?(?P<max>\d+)\}'

    max = int(t.lexer.lexmatch.group('max'))
    min = int(t.lexer.lexmatch.group('min')) if t.lexer.lexmatch.group('min') else max

    t.value = RegexRange(min, max)

    return t

t_CHAR = r'[^' + re.escape(literals) + r'\\' + r']'

# char_or_escape = r'(' + t_CHAR + r'|' + escaped + r')'
# class_regex = r'\[(' + char_or_escape + r'|' + char_or_escape + r'-' + char_or_escape + r')\]'
# @TOKEN(class_regex)
# def t_CLASS(t):


lexer = lex.lex()
