from __future__ import print_function
from future_builtins import *
import p_pytutor
import p_quiztutor
import sys

__all__ = [ 'parse']

def parse(src):
    """Return the parsed PlasTeX from source src."""

    from StringIO import StringIO
    from plasTeX.TeX import TeX

    # All plastex packages startswith p_<package name>
    pkgs = [ (k[2:], v) for (k, v) in globals().items() if k.startswith('p_') ]
    old_pkgs = [ (k, sys.modules.get(k, None)) for (k, v) in pkgs ]
    try:
        #TODO: grabbing input does not seems to work
        old_std = sys.stderr, sys.stdout
        sys.stderr = sys.stdout = StringIO()
        for k, pkg in pkgs:
            sys.modules[k] = pkg
        f_src = StringIO(unicode(src))
        f_src.name = '<string>'
        return TeX(file=f_src).parse()
    finally:
        sys.stderr, sys.stdout = old_std
        for k, pkg in old_pkgs:
            if pkg:
                sys.modules[k] = pkg
            else:
                # pkg is None
                del sys.modules[k]

if __name__ == '__main__':
    print('start parsing...')
    print(parse('\\usepackage{pytutor}\\begin{multiplechoice}sadasdas\\end{multiplechoice}'))
