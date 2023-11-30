Expresiones regulares:
R -> U
R -> ''

Uniones:
U -> C | U
U -> C

Concatenaciones:
C -> O C
C -> O

Valores con operadores unarios opcionales:
O -> V *
O -> V +
O -> V ?
O -> V range
O -> V

Valores (caracteres, clases especiales, clases o caracteres escapados):
V -> [ S ]
V -> ( R )
V -> cls_d
V -> cls_w
V -> char
V -> escaped
V -> cls_int

Sets de clases:
S -> A S
S -> ''

Atomos de clases:
A -> char
A -> escaped
A -> cls_int
