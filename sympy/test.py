from __future__ import division
from sympy import *
x = symbols('x')
y = symbols('y')
z = symbols('z')
# k, m, n = symbols('k m n', integer=True)
# f, g, h = symbols('f g h', cls=Function)


# a = 4*x*y*z + 3*y*x*z + 2*z*x*y + 2 + 3

#b = "((x-1)(x-2))/(x-1)"

print(simplify((x**3 + x**2 - x - 1)/(x**2 + 2*x + 1)))


