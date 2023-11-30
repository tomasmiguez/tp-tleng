from lexer import RegexClassInterval, tokens
from .errors import SyntaxError
from ply.yacc import yacc
from regex import Char, Concat, Empty, Lambda, Plus, Star, Union


def _enum_to_union(enum):
    union = Empty()
    for sym in enum:
        union = Union(union, Char(sym))
    return union


def p_regex_union(p):
    '''
    regex : union
    '''
    p[0] = p[1]


def p_regex_lambda(p):
    '''
    regex :
    '''
    p[0] = Lambda()


def p_union(p):
    '''
    union : concat '|' union
    '''
    p[0] = Union(p[1], p[3])


def p_union_concat(p):
    '''
    union : concat
    '''
    p[0] = p[1]


def p_concat(p):
    '''
    concat : op concat
    '''
    p[0] = Concat(p[1], p[2])


def p_concat_lambda(p):
    '''
    concat : op
    '''
    p[0] = p[1]


def p_op(p):
    '''
    op : val '*'
       | val '+'
       | val '?'
       | val
    '''
    if len(p) == 3:
        if p[2] == '*':
            p[0] = Star(p[1])
        elif p[2] == '+':
            p[0] = Plus(p[1])
        elif p[2] == '?':
            p[0] = Union(p[1], Lambda())
    else:
        p[0] = p[1]


def p_op_range(p):
    '''
    op : val RANGE
    '''
    unions = Empty()
    for n in range(p[2].min, p[2].max + 1):
        concats = Lambda()
        for _ in range(n):
            concats = Concat(concats, p[1])
        unions = Union(unions, concats)
    p[0] = unions


def p_val_union_set(p):
    '''
    val : '(' regex ')'
        | '[' set ']'
        | esp
    '''
    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = p[1]


def p_val_class_digit(p):
    '''
    val : CLS_D
    '''
    _class_digit = _enum_to_union(RegexClassInterval('0', '9').all_symbols)

    p[0] = _class_digit


def p_val_class_word(p):
    '''
    val : CLS_W
    '''
    _class_word_symbols = RegexClassInterval('a', 'z').all_symbols
    _class_word_symbols = _class_word_symbols.union(
        RegexClassInterval('A', 'Z').all_symbols
    )
    _class_word_symbols = _class_word_symbols.union(
        RegexClassInterval('0', '9').all_symbols
    )
    _class_word_symbols = _class_word_symbols.union({'_'})

    _class_word = _enum_to_union(_class_word_symbols)

    p[0] = _class_word


def p_val_int(p):
    '''
    val : CLASS_INT
    '''
    p[0] = Concat(Concat(Char(p[1].fst), Char('-')), Char(p[1].lst))


def p_set(p):
    '''
    set : atom set
    '''
    p[0] = Union(p[1], p[2])


def p_set_lambda(p):
    '''
    set :
    '''
    p[0] = Empty()


def p_atom_esp(p):
    '''
    atom : esp
    '''
    p[0] = p[1]


def p_atom_int(p):
    '''
    atom : CLASS_INT
    '''
    if ord(p[1].fst) > ord(p[1].lst):
        raise SyntaxError(f'Invalid range {p[1]}')
    unions = Empty()
    for sym in p[1].all_symbols:
        unions = Union(unions, Char(sym))
    p[0] = unions


def p_esp(p):
    '''
    esp : CHAR
        | ESCAPED
    '''
    p[0] = Char(p[1])


def p_error(p):
    if p:
        raise SyntaxError(f'Unexpected token {p.value!r} at position {p.lexpos}')
    else:
        raise SyntaxError(f'Unexpected end of expression')


parser = yacc()
