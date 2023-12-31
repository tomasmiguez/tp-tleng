from lexer import RegexClassInterval, tokens
from .errors import SyntaxError
from ply.yacc import yacc
from regex import Char, Concat, Empty, Lambda, Plus, RegClass, Star, Union

_class_digit_symbols = RegexClassInterval('0', '9').all_symbols

_class_word_symbols = RegexClassInterval('a', 'z').all_symbols
_class_word_symbols = _class_word_symbols.union(
    RegexClassInterval('A', 'Z').all_symbols
)
_class_word_symbols = _class_word_symbols.union(
    RegexClassInterval('0', '9').all_symbols
)
_class_word_symbols = _class_word_symbols.union({'_'})


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


def p_op_kleene(p):
    '''
    op : val '*'
    '''
    p[0] = Star(p[1])


def p_op_positive(p):
    '''
    op : val '+'
    '''
    p[0] = Plus(p[1])


def p_op_optional(p):
    '''
    op : val '?'
    '''
    p[0] = Union(p[1], Lambda())


def p_op_id(p):
    '''
    op : val
    '''
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


def p_val_set(p):
    '''
    val : '[' set ']'
    '''
    p[0] = RegClass(p[2])


def p_val_regex(p):
    '''
    val : '(' regex ')'
    '''
    p[0] = p[2]


def p_val_esp(p):
    '''
    val : CHAR
        | ESCAPED
    '''
    p[0] = Char(p[1])


def p_val_class_digit(p):
    '''
    val : CLS_D
    '''
    p[0] = RegClass(_class_digit_symbols)


def p_val_class_word(p):
    '''
    val : CLS_W
    '''
    p[0] = RegClass(_class_word_symbols)


def p_val_int(p):
    '''
    val : CLS_INT
    '''
    p[0] = Concat(Concat(Char(p[1].fst), Char('-')), Char(p[1].lst))


def p_set(p):
    '''
    set : atom set
    '''
    p[0] = p[1].union(p[2])


def p_set_lambda(p):
    '''
    set :
    '''
    p[0] = set()


def p_atom_esp(p):
    '''
    atom : CHAR
         | ESCAPED
    '''
    p[0] = {p[1]}


def p_atom_int(p):
    '''
    atom : CLS_INT
    '''
    if ord(p[1].fst) > ord(p[1].lst):
        raise SyntaxError(f'Invalid range {p[1]}')

    p[0] = p[1].all_symbols


def p_error(p):
    if p:
        raise SyntaxError(f'Unexpected token {p.value!r} at position {p.lexpos}')
    else:
        raise SyntaxError(f'Unexpected end of expression')


parser = yacc()
