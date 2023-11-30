from lexer import tokens
from ply.yacc import yacc
from tlengrep.regex import Char, Concat, Empty, Lambda, Plus, Star, Union

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
    concat :
    '''
    p[0] = Lambda()

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
    p_op_range : val RANGE
    '''
    unions = Empty()
    for n in range(p[2].min, p[2].max):
        concats = Lambda()
        for _ in range(n):
            concats = Concat(concats, p[1])
        unions = Union(unions, concats)
    p[0] = unions

def p_val_paren(p):
    '''
    val : '(' union ')'
    '''
    p[0] = p[2]

def p_val_char(p):
    '''
    val : CHAR
        | ESCAPED
    '''
    p[0] = Char(p[1])

def p_val_class(p):
    '''
    val : CLASS
    '''
    unions = Empty()
    for sym in p[1].all_symbols:
        unions = Union(unions, Char(sym))
    p[0] = unions

def p_error(p):
    if p:
        raise ParseError(
            f'Unexpected token {p.value!r} at position {p.lexpos}')
    else:
        raise ParseError(f'Unexpected end of expression')

class ParseError(Exception):
    pass

parser = yacc()
