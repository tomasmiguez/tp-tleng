Uniones:
U -> C | U
U -> C

Concatenaciones:
C -> O C
C -> ''

Valores con operadores unarios opcionales:
O -> V *
O -> V +
O -> V ?
O -> V rg
O -> V

Valores (caracteres, clases especiales, clases o caracteres escapados):
V -> [ CL ]
V -> ch
V -> esc
V -> ( U )

Clases de caracteres:
CL -> CLA CL
CL -> ''

CLA -> CE
CLA -> cls_int

CE -> ch
CE -> esc
