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

    @property
    def all_symbols(self) -> set:
        return set([chr(i) for i in range(ord(self.fst), ord(self.lst) + 1)])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RegexClassInterval):
            return False

        return self.fst == other.fst and self.lst == other.lst


tokens = (
    'CHAR',
    'ESCAPED',
    'RANGE',
    'CLS_INT',
    'CLS_D',
    'CLS_W',
)

literals = "|*+?()[]"


def t_RANGE(t):
    r'\{(?:(?P<min>\d+),)?(?P<max>\d+)\}'

    max = int(t.lexer.lexmatch.group('max'))
    min = int(t.lexer.lexmatch.group('min')) if t.lexer.lexmatch.group('min') else max

    t.value = RegexRange(min, max)

    return t


t_CHAR = r'[^' + re.escape(literals) + r'\\' + r']'

escaped = r'\\([^dw])'
char_or_escape = r'(?:' + t_CHAR + r'|' + escaped + r')'
class_int = r'(?P<fst>' + char_or_escape + r')-(?P<lst>' + char_or_escape + r')'


@TOKEN(class_int)
def t_CLS_INT(t):
    fst = t.lexer.lexmatch.group('fst').lstrip('\\')
    lst = t.lexer.lexmatch.group('lst').lstrip('\\')
    t.value = RegexClassInterval(fst, lst)

    return t


@TOKEN(escaped)
def t_ESCAPED(t):
    t.value = t.lexer.lexmatch.group(10)
    return t


t_CLS_D = r'\\d'
t_CLS_W = r'\\w'

lexer = lex.lex()
