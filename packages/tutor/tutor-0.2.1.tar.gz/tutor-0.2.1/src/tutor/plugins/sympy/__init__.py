sum_ = sum
from sympy.abc import *
from sympy import *
import sympy as sp
from tutor.visualization.filters import tex_finalize
sum, sum_ = sum_, sum #@ReservedAssignment

#===============================================================================
# Render sympy objects
#===============================================================================
@tex_finalize.dispatch(Basic)
def _sympy_latex(obj, **kwds):
    return latex(obj)

#===============================================================================
# Constants
#===============================================================================
Zero, One, Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten = map(Integer, range(11))
Half = One / 2

ii, jj, kk = symbols('i,j,k', each_char=False)

if __name__ == '__main__':
    print tex_finalize(x ** 2 + y ** 2 / 2)
    print tex_finalize(3 ** (One / 2) / 5)
