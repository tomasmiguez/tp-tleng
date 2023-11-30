import re
import ply.lex as lex
from ply.lex import TOKEN

class RegexRange:
    def __init__(self, min: int, max: int) -> None:
        self.min = min
        self.max = max

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RegexRange):
            return False

        return self.min == other.min and self.max == other.max

class RegexClassInterval:
    def __init__(self, fst: str, lst: str) -> None:
        self.fst = fst
        self.lst = lst

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RegexClassInterval):
            return False

        return self.fst == other.fst and self.lst == other.lst

tokens = (
    'CHAR',
    'ESCAPED',
    'RANGE',
    'CLASS_INT',
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

char_or_escape = r'(?:' + t_CHAR + r'|' + escaped + r')'
class_int = r'(?P<fst>' + char_or_escape + r')-(?P<snd>' + char_or_escape + r')'
@TOKEN(class_int)
def t_CLASS_INT(t):
    t.value = RegexClassInterval(t.lexer.lexmatch.group('fst'), t.lexer.lexmatch.group('snd'))
    return t

lexer = lex.lex()
