Uniones:
U -> C | U
U -> C

Concatenaciones:
C -> VO C
C -> ''

Valores con operadores unarios opcionales:
VO -> V O

Operadores unarios opcionales:
O -> *
O -> +
O -> { n }
O -> { n , n }
O -> ''

Valores (caracteres, clases especiales, clases o caracteres escapados):
V -> [ CL ]
V -> char
V -> number
V -> escaped

Clases de caracteres:
CL -> CLA CL
CL -> ''

Atomo de clase de caracteres:
CLA -> char - char
CLA -> char
