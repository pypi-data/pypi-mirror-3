from maple import *
import sys
from cStringIO import StringIO
from tutor.transforms.var_filters import latex_register as _latex_register
from tutor.plugins.complexity import *

@_latex_register(core.Maple)
def _maple_to_latex(obj, **kwds):
    old = sys.stdout
    sys.stdout = StringIO()
    is_vec = (M.has(obj, ii) or M.has(obj, jj) or M.has(obj, kk))
    if is_vec:
        obj = M.collect(M.collect(M.collect(obj, ii), jj), kk)

    try:
        M.latex(obj)
        out = sys.stdout.getvalue()
        out = out.rstrip('\n')
        out = out.strip()
        out = out.replace('\f', '\\f') #TODO: fix output 
    finally:
        sys.stdout = old

    # Support vector functions
    if is_vec:
        for c in 'ijk':
            out = out.replace('{\\it \\_%s}' % c, '\\mathbf{%s}' % c)
    return out

M("""
`latex/latex/numeric` := proc(e)
local texlist, `\\frac `, `-`, `/`, `{`, `}`, ll;
      if e = Float(infinity) then
        texlist := `{\\it Float}(\\infty )`
       elif e = Float(-infinity) then
        texlist := `{\\it Float}(-\\infty )`
       elif e = Float(undefined) then
        texlist := `{\\it Float(undefined)}`
       elif e = undefined then
        texlist := `{\\it undefined}`
       elif e < 0 or type(e,negzero) then
        texlist := `-`, `latex/latex/numeric`(-e)
       elif type(e,'integer') then
        texlist := e
       elif type(e,'float') then
        texlist := `latex/latex/float`(e)
       elif type(e,'fraction') then
        texlist := `{`, `\\frac `, `{`, op(1,e), `}`, `{`, op(2,e), `}`, `}`        
       elif e = infinity then
        texlist := `\\infty `
       end if;
      ll := LaTeX:-CheckLineBreak([texlist]);
      texlist, ll
end proc:""")


#from sage.interfaces.maple import MapleElement
#
## Creates the M class
#class _M(object):
#    def __init__(self, M):
#        self.M = M
#    def __call__(self, *args, **kwds):
#        return self.M(*args, **kwds)
#    def __getattr__(self, attr):
#        return self.M(attr)
#M = _M(maple)
#
## Let python multiplication maps to commutative multiplication
#def _mul(self, right):
#
#    P = self._check_valid()
#    try:
#        return P.new('%s * %s' % (self._name, right._name))
#    except Exception, msg:
#        raise TypeError, msg
#
#MapleElement._mul_ = _mul
#
## Comparisons should work the maple way!
#def _op(symb):
#    def my_op(self, right=None):
#        if not isinstance(right, MapleElement):
#            right = _maple(right)
#
#        P = self._check_valid()
#        try:
#            return P.new('%s %s %s' % (self._name, symb, right._name))
#        except Exception, msg:
#            raise TypeError, msg
#    return my_op
#
#del MapleElement.__cmp__
#MapleElement.__eq__ = _op('=')
#MapleElement.__lt__ = _op('<')
#MapleElement.__le__ = _op('<=')
#MapleElement.__gt__ = _op('>')
#MapleElement.__ge__ = _op('>=')
#MapleElement.__ne__ = _op('<>')

ii, jj, kk = map(M, '_i _j _k'.split())
x, y, z, t, i, j, k = map(M, 'x y z t i j k'.split())

def dot_prod(u, v):
    coeff = M.coeff
    return (coeff(u, ii) * coeff(v, ii)
             + coeff(u, jj) * coeff(v, jj)
             + coeff(u, kk) * coeff(v, kk))

def vec_prod(u, v):
    coeff = M.coeff
    ux, uy, uz = coeff(u, ii), coeff(u, jj), coeff(u, kk)
    vx, vy, vz = coeff(v, ii), coeff(v, jj), coeff(v, kk)
    return ((uy * vz - uz * uy) * ii
             + (uz * vx - ux * uz) * jj
             + (ux * vy - uy * ux) * kk)

def arr_prod(u, v):
    coeff = M.coeff
    return (coeff(u, ii) * coeff(v, ii) * ii
             + coeff(u, jj) * coeff(v, jj) * jj
             + coeff(u, kk) * coeff(v, kk) * kk)

# Numbers
One, Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten = map(M, range(1, 11))
Half, Third = M(1) / 2, M(1) / 3
pi = Pi
diff = M.diff
oo = M.infinity

if __name__ == '__main__':
    from pprint import pprint
    from tutor.transforms import var_filters
    res = x * ii / 2 + y * jj
    print M('diff')(x ** 2, x)
    print M.diff(x ** 2, x)

    print (var_filters.latex(x ** 2 / 2 * ii - (y + 1) ** 2 * jj))
