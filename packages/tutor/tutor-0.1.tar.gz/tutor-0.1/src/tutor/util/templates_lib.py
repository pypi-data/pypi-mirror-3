#-*- coding: utf8 -*-
# Py3K compatilibity
from __future__ import absolute_import
from __future__ import print_function
from future_builtins import *
import os
import pickle
import subprocess
from simpleparse.parser import Parser

__package__ = 'tutor.common'
import tutor
import tutor.common
from ..common import tutor_config as config

#------------------------------------------------------------------------------#
#
#   API Functions
#
#------------------------------------------------------------------------------#
__all__ = ['run', 'compile']
def run(addr, ntries=10):
    """Loads and execute the executable python template at address 'addr'. It 
    also compiles the template if it is not already compiled.
    
    Input
    -----
    
    addr (string): path to executable template in the library
    
    Output
    ------
    
    a string buffer object with the dump from the template file.
    """

    addr = expand_addr(addr)
            
    # check if script exists
    if os.path.isfile(addr + '.py'):
        fname = addr + '.py'
    elif os.path.isfile(addr + '.tex') or os.path.isfile(addr + '.lyx'):
        compile(addr)
        return run(addr, ntries=ntries)
    else:
        raise OSError("Invalid address: '%s'" % addr)    
    
    # run script
    args = ['python', fname]
    f = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    err = f.stderr.read()
    #if not 'AssertionError' in err:
    #    ntries = 0
    if err:
        if ntries > 0:
            return run(addr, ntries - 1)
        else:
            msg = "Script for model '%s' terminated with the error message.\n"
            msg += '-' * 79 + '\n' + err
            raise RuntimeError(msg)
    
    # reconstruct tex file
    tex = f.stdout.readlines()
    tex = ''.join(tex)
    return tex
    
def compile(addr):
    """Compiles (or re-compile, it is already compiled) the template at 
    address 'addr' and saves it to the library.
    
    Input
    -----
    
    addr (string): path to executable template in the library

    """
    
    addr = expand_addr(addr)
    
    # read content from library file
    try:
        if os.path.isfile(addr + '.tex'):
            F = open(addr + '.tex')
        elif os.path.isfile(addr + '.lyx'):
            os.system('lyx -e latex %s.lyx' % addr)
            F = open(addr + '.tex')
        else:
            raise OSError('Invalid address: %s' % addr)
        data = F.read()    
    finally:
        if 'F' in dir():
            F.close()
      
    # compile data into a script
    data = parse_data(pre_parser, data)
    data = parse_data(parser, data)

    # save script file
    with open(addr + '.py', 'w') as F:
        F.write(u"#-*- coding: utf-8 -*-\n")
        F.write(u"from tutor.scripts import default_namespace as _TNS_\n")
        F.write(u"from tutor.scripts.default_namespace import *\n")
        #F.write(u"self = _TNS_.get_self()\n")
        F.write(data)
        #F.write(u"\n_TNS_.print_('\\n%%%s\\n')" % config.SCRIPT_SEPARATOR_STRING)
        #F.write(u"\n_TNS_.dump(self)")

#------------------------------------------------------------------------------#
#
#   generic helpers
#
#------------------------------------------------------------------------------#
def expand_addr(addr):
    if addr.startswith(config.TEMPLATE_ITEM_LIB_PATH):
        return addr
    else:
        return os.path.join(config.TEMPLATE_ITEM_LIB_PATH, addr)
        
#------------------------------------------------------------------------------#
#
#   compile() helpers
#
#------------------------------------------------------------------------------#
def parse_data(parser, data):
    """auxiliary parser loop function used in pre-parsing and parsing"""
    
    parsed = parser.parse(data)
    #pprint.pprint(parsed)
    Q = []
    for obj in parsed[1]:
        obj_data = data[obj[1]:obj[2]]
        transformation = getattr(parser, obj[0])
        Q.append(transformation(obj_data))
        
    return ''.join(Q)

# Declare pre-parser grammar --------------------------------------------------#
def other(data):
    """Process 'other' segments in pre-parsing phase."""
    return data
        
def choice(data):
    """Process 'choice' segments in pre-parsing phase."""
    
    return data
    
def env(data):
    """Process 'env' segments in pre-parsing phase."""
    
    env = data[6:].strip(' {}')
    return data
    
pre_declaration = r'''
env            := '\\begin', ' '*, '{', ' '*, ('multiplechoice'/'truefalse'), ' '*, '}' 
choice         := '\\choice', ' '*, '{', -'}'*, '}'
other          := -(env/choice)*
root           := (env/choice/other)*
'''

pre_parser = Parser(pre_declaration)
pre_parser.other = other
pre_parser.choice = choice
pre_parser.env = env

# Declare the 2nd parser grammar ----------------------------------------------#
def other(data):
    data = data.replace('\\', '\\\\')
    return "\n_TNS_.print_(u'''%s''')\n" % data

def python(data):
    # strip begin and end
    data = data[14:-12]
    data = data.splitlines()
    n_ws = min([ len(l) - len(l.lstrip()) for l in data ])
    data = [ l[n_ws:] for l in data ]
            
    # insert code as is in python block
    data = '\n'.join(data)
    return '\n#\n# *CODE INSIDE A PYTHON ENVIRONMENT* \n#\n%s\n# *END PYTHON ENVIRONMENT*\n' % (data)
    
def py(data):
    data = data[4:-1]
    
    # print the result of evaluation
    return '\n# *PY COMMAND*\n_TNS_.print_(%s)\n# *END PY COMMAND*\n' % data
    
def pyesc(data):
    data = data[7:-1]
    #TODO: escape data
    return py(''.join(['\py{', data, '}']))

declaration = r'''
python         :=  '\\begin{python}', -'\\end{python}'*,'\\end{python}'
py             :=  '\\py{', -'}'*, '}'
pyesc          :=  '\\pyesc{', -'}'*, '}'
comment        :=  '%',-'\n'*,'\n'
other          := -(python/py/comment/pyesc)*
root           := [ \n\t]*, (python/py/comment/pyesc/other)+
'''

parser = Parser(declaration)
parser.other = other
parser.python = python
parser.py = py
parser.pyesc = pyesc

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        addr = 'model'
        addr = 'limite1'
        addr = 'plano_tangente'
        #addr = 'regra_da_cadeia2'
    else:
        addr = sys.argv[1]
    compile(addr)
    buf = run(addr)
    print(buf)
