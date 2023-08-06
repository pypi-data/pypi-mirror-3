from __future__ import print_function
from future_builtins import * #@UnusedWildImport
import codecs
import sys
import p_pytutor #@UnusedImport
import p_quiztutor #@UnusedImport
from plasTeX.TeX import TeX
from plasTeX.Logging import getLogger, CRITICAL, disableLogging
from fs.tempfs import TempFS

__all__ = ['parse', 'disableLogging']

def parse(src, encoding=None, disp=False):
    """Return the parsed PlasTeX from source src."""
    # plasTeX display some annoying messages when it loads
    # modules. This can be disabled by disabling the logger
    # responsible for these messages (named 'status')
#    if not disp:
#        logger = getLogger('status')
#        logger.setLevel(CRITICAL)

    # All plastex packages startswith p_<package name>
    pkgs = [ (k[2:], v) for (k, v) in globals().items() if k.startswith('p_') ]
    old_pkgs = [ (k, sys.modules.get(k, None)) for (k, v) in pkgs ]

    try:
        # Configure packages
        for k, pkg in pkgs:
            sys.modules[k] = pkg

        # Set correct data encoding
        if isinstance(src, unicode):
            data = src.encode('utf8')
        else:
            if encoding != 'utf8':
                data = src.decode(encoding or 'ascii')
                data = data.encode('utf8')

        # Temporary file to hold data
        try:
            tmp = TempFS()
            with tmp.open('main.tex', 'w') as F:
                F.write(data)

            tmp_path = tmp.getsyspath('main.tex')
            with codecs.open(tmp_path, encoding='utf8') as F:
                tex = TeX(file=F)
                result = tex.parse()

        finally:
            del tmp
        return result
    finally:
        for k, pkg in old_pkgs:
            if pkg:
                sys.modules[k] = pkg
            else:
                del sys.modules[k]

if __name__ == '__main__':
    print('start parsing...')
    print(parse('\\documentclass{article}\\usepackage{pytutor}\\begin{document}Test\\end{document}'))
