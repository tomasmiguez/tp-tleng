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
O -> V rg
O -> V

Valores (caracteres, clases especiales, clases o caracteres escapados):
V -> [ CS ]
V -> cls_d
V -> cls_w
V -> ( R )
V -> CE
V -> cls_int

Sets de clases:
CS -> CA CS
CS -> ''

Atomos de clases:
CA -> CE
CA -> cls_int

Clases especiales:
CE -> ch
CE -> esc
