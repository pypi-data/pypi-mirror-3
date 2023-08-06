#-*- coding: utf8 -*-
'''Namespace objects are callable objects that return a dictionary of 
{names: values} that can be used to format other objects such as questions, 
subquestions, etc. 

Example
-------
 
>>> ns = CodeNS('a = 1; b = 2')
>>> ns()
{'a': 1, 'b': 2}
 
>>> render = ns.new_renderer()
>>> print(render('a=||a|| and b=||b||'))
a=1 and b=2
'''
from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.types' #@ReservedAssignment
    import tutor.types #@UnusedImport

import sys
import warnings
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from ..util.module_creation import new_module

class Namespace(object):
    def __call__(self):
        raise NotImplementedError('must be implemented in subclasses')

    def new_renderer(self):
        '''Return a function that renders strings using a randomly created 
        namespace.'''

        from ..visualization import render_template
        ns = self()
        def renderer(st, *args, **kwds):
            return render_template(st, 'latex', ns, *args, **kwds)
        return renderer

class CodeNS(Namespace):
    '''Namespace are callable objects that return namespace dictionaries from 
    the a given Python code
    '''

    def __init__(self, code):
        self.exec_modified = True
        if isinstance(code, str):
            code = code.decode('utf8')
        self.code = code

        # Remove all comment and empty lines from code
        code = code.splitlines()
        code = [ l for l in code if l.strip() and not l.startswith('#') ]

        # Separate all import lines
        imports = ['\n']
        for l in code:
            if l.startswith('from ') or l.startswith('import '):
                imports.append(l)
            else:
                break
        code = code[len(imports) - 1:]

        # Indent code and put it into the _pytutor_generate_namespace() function
        code = '\n'.join([ '    ' + l for l in code ])
        code = '\ndef _pytutor_generate_namespace():\n%s\n    return locals()' % code

        # Add a line importing a inert display_block
        imports.append('from tutor.util.inert_commands import display_block\n')
        code = '\n'.join(imports) + code

        self.new_code = '#-*- coding: utf8 -*-\n' + code
        self._module = new_module(code.encode('utf8'))
        self._func = self._module._pytutor_generate_namespace

    def __call__(self):
        stdold = sys.stderr, sys.stdout
        sys.stderr = sys.stdout = temp = StringIO()
        last_ex = None
        try:
            if self.exec_modified:
                for _ in range(50):
                    try:
                        return self._func()
                    except Exception as last_ex:
                        pass
                else:
                    self.exec_modified = False

            if not self.exec_modified:
                warnings.warn('code is running non-optimized!')
                for _ in range(30):
                    try:
                        module = new_module(self.code)
                        return vars(module)
                    except Exception as last_ex:
                        pass

        finally:
            sys.stderr, sys.stdout = stdold

        if last_ex is not None:
            msg = ['\n\nError caught executing code',
                   '---------------------------\n\n',
                   self.new_code,
                   '\n\nCaptured output:\n',
                   temp.getvalue(),
                   '\n\n%s: %s' % (type(last_ex).__name__, last_ex)]
            raise RuntimeError('\n'.join(msg))

if __name__ == '__main__':
    print(CodeNS(
'''#Strip these cómments
foo = 1
bar = 2''')())

    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)
