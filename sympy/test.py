from __future__ import division
from sympy import *
x = symbols('x')
y = symbols('y')
z = symbols('z')
# k, m, n = symbols('k m n', integer=True)
# f, g, h = symbols('f g h', cls=Function)

a = -x + 3*x + 2*x + 2 + 3

#b = 2*x*x
print("b: ", a)
print(srepr(a))
# print("Str expr: ", str_expr)
# a = sympify(str_expr)
# print("Result: ", a)


# simplify(a)