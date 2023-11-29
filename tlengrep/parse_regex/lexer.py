import re
import ply.lex as lex
from ply.lex import TOKEN

class RegexRange:
    def __init__(self, min: int, max: int) -> None:
        self.min = min
        self.max = max

tokens = (
    'CHAR',
    'ESCAPED',
    'RANGE',
    'CLASS',
)

literals = "|*+?()"

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

t_CHAR = r'[^' + re.escape(literals) + r'\\\[\]]'

# char_or_escape = r'(' + t_CHAR + r'|' + escaped + r')'

# t_CLASS = r'\[(' + char_or_escape + r'|' + char_or_escape + r'-' + char_or_escape + r')\]'

lexer = lex.lex()
