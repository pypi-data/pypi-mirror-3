#-*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from future_builtins import *
import re
import os
import sys
import datetime
import tutor.plastex
import tutor.common
from cStringIO import StringIO

#------------------------------------------------------------------------------
#                   CONVERTERS --- LATEX TO PYTHON
#------------------------------------------------------------------------------
def latex_to_py(path, name):
    """
    Loads latex file at address in name and return a python script 
    corresponding to that file.
    """

    # loads latex source
    base = tutor.common.config.TEMPLATE_QUESTION_LIB_PATH
    path = os.path.join(base, path)
    with open(path) as F:
        src = F.read()
        # avoid plastex bug by inserting extra whitespace
        src = src.replace('\\begin{truefalse}', '\\begin{truefalse}\n\n')
        src = src.replace('\\begin{multiplechoice}', '\\begin{multiplechoice}\n\n')
    return latex_src_to_py(src, path, name)

def mixed_to_py(path_py, path_tex, name):
    """
    Merges python script at path 'path_py' with latex template in 'path_tex' and 
    and return a python script corresponding to both files.
    """
    pass

#------------------------------------------------------------------------------
#                               AUXILIARY FUNCTIONS
#------------------------------------------------------------------------------
def extract_metadata(parsed):
    """Extract metadata from a latex parse tree. Returns a dictionary holding 
    this metadadata"""

    meta = parsed.getElementsByTagName('metadata')
    if len(meta) == 1:
        meta = meta[0].attributes['content']
        meta = [ c for c in meta.childNodes if not isinstance(c, basestring) ]
        for obj in meta:
            key = obj.tagName
            data = obj[0].childNodes[0].strip()
            
            # format data according to metadata key
            if key == 'creationdate':
                data = data.split('/')
                data.reverse()
                data = datetime.date(*map(int, data))
            elif key == 'time':
                mul = 1
                if data[-1].isalpha():
                    mul_factor = data[-1]
                    mul = { 'm': 1, 'h': 60, 'd': 60*24 }[mul_factor]
                    data = data[:-1]
                data =  float(data) * mul 
            elif key == 'status':
                data = ( idx for (idx, v) in STATUS_CHOICES if v == data ).next() 
            elif key == 'itemtype':
                data = ( idx for (idx, v) in TYPE_CHOICES if v == data ).next() 
            elif key == 'difficulty':
                data = ( idx for (idx, v) in DIFFICULTY_CHOICES if v == data ).next()
            elif key == 'author':
                data = data
            else:
                raise RuntimeError("Unrecognized key '%s'" % key)
            
            # save metadata key
            setattr(template, key, data)
    elif len(meta) == 0:
        pass
    else:
        raise tutor.plastex.LaTeXError('Expect only one \metadata command in LaTeX file, got %s' % len(meta))


def process_document_obj(obj):
    if isinstance(obj, unicode):
        st = obj.strip()
        if st:
            return '# LaTeX: ' + obj
        else:
            return None
    elif obj.tagName == 'python':
        src = obj.source
        src = src[14:-12]
        return '#\\begin{python} code block\n%s\n#\\end{python}' % src
    elif obj.tagName == 'itembody':
        return '\n'.join( process_itembody_node(node) for node in obj )
    else:
        raise ValueError("Unrecognized object '%s'" % obj)
    
def process_choices(node):
    res = []
    
    # check if a \solution node exists
    if node[0].tagName == 'solution':
        solution = node[0]
        nodes = node.childNodes[1:]
    else:
        solution = None
        nodes = node.childNodes
    
    # save solution
    if solution:
        solution = solution.source[9:].strip()
        pre, data = get_py_src(solution)
        if pre:
            res.append(pre)
        res.append('PY_NODE.solution = %s' % data)
        
    # save choices
    while nodes:
        # process choices
        node = nodes.pop(0)
        grade, _, choice = node.source.strip().partition('}')
        __, _, grade = grade.partition('{')
        grade = { 'f': 0, 't': 1, 'v': 1, '*': 1, 'key': 1, '': 0 }.get(grade.lower(), grade)
        res.append('\nPY_CHOICE = Choice(grade=%s)' % grade)
        
        # save choice data
        pre, data = get_py_src(choice.strip())
        if pre:
            res.append(pre)
        res.append('PY_CHOICE.choice = %s' % data)
        
        # extract explanation
        if nodes[0].tagName == 'explanation':
            expl = nodes.pop(0).source.strip()
            expl = expl[12:].strip()
            pre, data = get_py_src(expl)
            if pre:
                res.append(pre)
            res.append('PY_CHOICE.explanation = %s' % data)
        
        res.append('PY_NODE.add_choice(PY_CHOICE)')
        
    return '\n'.join(res)
    
def process_itembody_node(node):
    if getattr(node[0], 'tagName', None) == 'multiplechoice':
        res = process_choices(node[0])
        return '\nPY_NODE = MultipleChoice()\nPY_QUESTION.add_node(PY_NODE)\n' + res
    elif getattr(node[0], 'tagName', None) == 'truefalse':
        res = process_choices(node[0])
        return '\nPY_NODE = TrueFalse()\nPY_QUESTION.add_node(PY_NODE)\n' + res
    else:
        pre, data = get_py_src(node.source.strip())
        res = 'PY_QUESTION.add_node(DataNode(data=%s))' % data
        if pre:
            return pre + '\n' + res 
        else:
            return res
    
def unescape(cmd):
    """ remove símbolos latex/lyx para que cmd se torne um comando python válido"""
    
    cmd = cmd.replace('{*}', '*')
    cmd = cmd.replace('~', '    ')
    cmd = cmd.replace(r'\\', '\n')
    cmd = cmd.replace('{[}', '[').replace('{]}', ']')
    cmd = cmd.replace(r'\#', '#').replace(r'\_', '_').replace(r'\%', '%').replace(r'\,', ' ')
    cmd = cmd.replace(r'\{', '{').replace(r'\}', '}')
    cmd = cmd.replace(r'``', '"').replace("''", '"')
    cmd = cmd.replace(r'\textbackslash', r'\'')
    cmd = cmd.replace(r'\textcompwordmark', '')
    cmd = cmd.replace(r'\textquotedbl', '"') 
    cmd = cmd.replace('{}', '')
    cmd = cmd.replace('\n\n', '\n')
    cmd = cmd.replace('’', '\'')
    cmd = cmd.replace('”', "''")
    return cmd.strip()

PY_REGEX_PY = r'((\\py)\s*[{][^}]*[}])'
PYSRC_REGEX = re.compile(PY_REGEX_PY)

def get_py_src(src):
    # extract python objects from source
    pre = []
    data = repr(src)
    match = PYSRC_REGEX.search(src)
    while match:
        data = 'PY_AUX'
        if not pre:
            pre.append("PY_AUX = ( '' ")
        else:
            pre.pop()
            
        # partition src into header and body 
        i, j = match.span()
        header = src[:i]
        body = match.group()
        src = src[j:]
        
        # process body element
        _, __, body = body.rstrip('}').partition('{')
        body = body.strip()
        
        # body: check sign
        if body.startswith('+'):
            sign = 'True'
            body = body[1:].strip()
        else:
            sign = 'False'
        
        # body: check brackets
        if body.startswith('(('):
            bracket = 'True'
            body = body[2:-2].strip()
        else:
            bracket = 'False'
        
        # un-escape latex characters and fixes bug where plastex puts an
        # extra whitespace after an underscore
        body = unescape(body)
        body = body.replace('_ ', '_')
   
        # save all data
        pre.append('      + %s' % repr(header))
        pre.append('      + to_latex(%s, sign=%s, braces=%s)' % (body, sign, bracket))
        pre.append('      + %s' % repr(src))
        match = PYSRC_REGEX.search(src)
    
    # add extra newline to pre    
    if pre:
        pre.append(')')    
    return '\n'.join(pre), data

def latex_src_to_py(latex_src, path, name):
    """Returns python script corresponding to the LaTeX source in 'latex_src'.
    """ 
    
    py_src = ["#\n# Python script was automatically generated from file: \n#\t%s\n#"  % path,
              'from tutor.question import *\n'
              'from tutor.script import *\n'
              'from cStringIO import StringIO\n'
              'import sys\n'
              'PY_QUESTION = Question()\n'
              'PY_QUESTION_NAME = %s\n'
              'OLD_STDOUT, sys.stdout = sys.stdout, StringIO()\n' % repr(name) ]
    
    #TODO:FIXME plastex prints unwanted messages to stdout, stderr
    try:
        stdbckp = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = StringIO()
        parsed = tutor.plastex.parse(latex_src)
        parsed.normalize()
    finally:
        sys.stdout, sys.stderr = stdbckp
        print()
            
    # separate preamble from document
    preamble = parsed.preamble.source.replace('\n\n', '\n')
    document = parsed.getElementsByTagName('document')[0]
    py_src.append('PY_PREAMBLE = %s' % repr(preamble))
    for par in document:
        for obj in par:
            src = process_document_obj(obj)
            if not src is None:
                py_src.append(src)
    
    # commands that print the json representation of Question
    py_src.append('# Return jsonpickle representation of current question\n'
                  'import sys\n'
                  'import jsonpickle\n'
                  'sys.stdout = OLD_STDOUT\n'
                  'jsonobj = [ PY_QUESTION_NAME, PY_QUESTION.nodes ]\n'
                  "print('::JSON::\\n' + jsonpickle.encode(jsonobj))\n")
    return '\n\n'.join(py_src)

#------------------------------------------------------------------------------
#                   CONVERTERS --- LYX TO PYTHON
#------------------------------------------------------------------------------
#
#
#
#



def lyx_to_py(path, name):
    '''Convert LyX file to latex and then to a python script'''
    pass


def xml_to_py(path, name):
    pass

