sum_ = sum
from tutor.plugins.complexity import *
from sympy.abc import *
from sympy import *
import sympy as sp
from tutor.transforms.var_filters import latex_register as _latex_register
sum, sum_ = sum_, sum

Zero, One, Two, Three, Four, Five, Six, Seven, Eight, Nine = map(Integer, range(10))
Half = One / 2

ii, jj, kk = symbols('i,j,k', each_char=False)


@_latex_register(Basic)
def _sympy_to_latex(obj, **kwds):
    return latex(obj)[1:-1]
