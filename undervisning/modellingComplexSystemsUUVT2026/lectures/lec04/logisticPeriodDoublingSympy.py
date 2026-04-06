"""Minimal SymPy computation for the logistic period doubling."""

import sympy as sp


# sp.symbols('...') creates symbolic variables that SymPy manipulates exactly,
# without introducing floating-point approximations.
# Symbols:
#   r, x are the original parameter and phase-space variables,
#   a, y are the local coordinates near the period-doubling point
#   (r, x) = (3, 2/3), i.e. r = 3 + a and x = 2/3 + y.
r, x, a, y = sp.symbols('r x a y')

# Logistic map f_r(x) = r x (1 - x).
f = r * x * (1 - x)

# f.subs(x, f) substitutes f in place of x, so it builds the composition
# f_r(f_r(x)).
# sp.expand(...) multiplies everything out into a polynomial form, which makes
# derivatives and coefficient extraction easier to read.
# Second iterate f_r^2(x). Period-2 points of f_r are fixed points of f_r^2.
f2 = sp.expand(f.subs(x, f))

# Local equation studied in the lecture:
#   G(a,y) = f_{3+a}^2(2/3 + y) - (2/3 + y).
# The quadratic part of G tells us the local geometry near period doubling.
# sp.Rational(2, 3) keeps the number 2/3 exact.
# .subs({...}) performs the change of variables r = 3 + a and x = 2/3 + y.
# A final sp.expand(...) rewrites the result as a polynomial in a and y.
G = sp.expand(
  f2.subs({
    r: 3 + a,
    x: sp.Rational(2, 3) + y
  }) - (sp.Rational(2, 3) + y)
)

# Print the full local polynomial and the derivatives used in the quadratic
# approximation from the slides.
# sp.diff(G, a, 2) means the second derivative d^2G/da^2.
# sp.diff(G, a, y) means first differentiate in a and then in y.
# .subs({a: 0, y: 0}) evaluates the symbolic derivative at the singular point.
print("G(a,y) =", G)
print("G_aa(0,0) =", sp.diff(G, a, 2).subs({a: 0, y: 0}))
print("G_ay(0,0) =", sp.diff(G, a, y).subs({a: 0, y: 0}))
print("G_yy(0,0) =", sp.diff(G, y, 2).subs({a: 0, y: 0}))
