#-*- coding: utf8 -*-
# This module implements the default namespace for template python scripts (it 
# is imported in scripts as '_TNS_'.  
#
#TODO: implement utility functions and a GLOBAL module that is imported directly
# on each script's namespace.
# 
#TODO: make the namespace 'pluggable', so user can add additional modules and 
# packages without having to load them explicitly in scripts.

# Py3K compatilibity list
from __future__ import absolute_import
from __future__ import print_function
from future_builtins import *
import sys as __sys
import pickle as __pickle
from maple import M, maple_misc
from cStringIO import StringIO

# fix latex default small frac printing behaviour
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


class _TNS_logger(list):
    # generic logger object that accepts any call and stores all calls made to 
    # self
    def __getattr__(self, attr):
        def logger_func(*args, **kwds):
            self.append((attr, args, kwds))
        return logger_func

def print_(obj, braces=False, sign=None):
    __sys.stdout.write(str_(obj, braces, sign).encode('utf8'))
    
def str_(obj, braces=False, sign=None):
    """Print objects to screen."""
    #TODO: specializes for more complicated types of objects/printing strategies
    #TODO: implement filters
    if isinstance(obj, basestring):
        return unicode(obj)
    elif isinstance(obj, tuple):
        return '\\left(' + ', '.join( str_(x) for x in obj ) + '\\right)'
    elif isinstance(obj, float):
        st = '%.2f' % obj
        if st.startswith('0.0'):
            st = '%.3f' % obj
            if st.startswith('0.00'):
                st = '%.4f' % obj
                if st == '0.0000':
                    st = '0.0'    
        return st
    else:
        # evaluate latex representation of maple expression
        out = StringIO()
        try:
            old_out = __sys.stdout
            __sys.stdout = out
            M.latex(obj)
        finally:
            __sys.stdout = old_out
        ret = out.getvalue()
        ret = ret.replace('\f', '\\f').rstrip('\n')
        
        if (braces and M.type(obj, M('`+`'))): # or (sign is None and ret.startswith('-')):
            braces = '\\left(%s\\right)'
            braces = '\\left[%s\\right]' if '\\left(' in ret else braces
            ret = braces % ret
        if sign:
            if ret.startswith('-'):
                if sign == '-':
                    return ' %s ' % ('+' + ret[1:])
                else:
                    return ' %s ' % ret
            ret = '%s' % (sign + ret)
        
        # subs _i, _j, and _k vectors
        ret = ret.replace('{\\it \\_i}', '\\mathbf{i}')
        ret = ret.replace('{\\it \\_j}', '\\mathbf{j}')
        ret = ret.replace('{\\it \\_k}', '\\mathbf{k}')
        
        return unicode(ret).strip()
    
def dump(obj):
    """Prints the output of pickle representing a given object as a comment 
    into the Latex file."""
    
    st = [ '% ' + l for l in  __pickle.dumps(obj).splitlines() ]
    print_('\n'.join(st))
    
def get_self():
    """Retrieves the 'self' object from argv."""
    
    if len(__sys.argv) == 2:
        return __pickle.loads(__sys.argv[1])
    else:
        return _TNS_logger()
        
#::: Funções matemáticas úteis :::::::::::::::::::::::::::::::::::::::::::::::::
_i, _j, _k = M('(_i, _j, _k)')


if __name__ == '__main__':
    print ('str_: ', str_(M('1/2 * sin(x) * log(x)')))
    R = _i + 2 * _j + 3 * _k
    N = _j - _k
    print(dot_prod(R, N))
    print(vec_prod(R, N))
    print(arr_prod(R, N))
    print(M(1))