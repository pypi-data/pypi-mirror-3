from __future__ import (absolute_import, print_function, unicode_literals, division)
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.visualization' #@ReservedAssignment
    import tutor.visualization #@UnusedImport
# ------------------------------------------------------------------------------

import collections
from functools import wraps

from ..util.multimethod import multimethod, anything
from ..util import pdfcreate #TODO: move this function here
from .template import render_tmpl_name
from .types import Renderer

#===============================================================================
# Main renderer
#===============================================================================
def render(obj, method='pprint', **kwds):
    '''
    
    Parameters
    ----------
    obj : object
        Sfdf.
    method : str
        Rendering method, can be 'repr', 'pprint', 'latex', or 'xhtml'. 
    '''

    if method == 'repr':
        return repr(obj, **kwds)
    else:
        try:
            renderer = RENDERERS[method]
        except KeyError:
            raise ValueError('rendering mode not supported: %s' % method)

        return renderer(obj, **kwds)

#===============================================================================
# Sub-renderers
#===============================================================================
@multimethod(anything)
def latex(obj, encoding='utf8', document=True, packages=None, required_packages=None, **kwds):
    '''All latex renderers accept the following arguments:
    
    Parameters
    ----------
    encoding : str
        Default is 'utf8'. Is the encoding of output data.
    document : bool
        If True, renders the object as a LaTeX document. Otherwise, it renders
        only the document part.
    packages : iterable
        A list of  packages in the preamble section of LaTeX document. Is 
        ignored if ``document`` is not True.
    required_packages : iterable
        A list that is passed to the rendering function in order to register 
        packages that are necessary to render the latex document. 
        '''

    if isinstance(obj, str):
        return obj.decode(encoding)
    return unicode(obj)

def latex_api(func):
    '''Implements support for the encoding, document, packages and 
    required_packages parameters of the latex() renderer.
    
    Expect an unicode output corresponding to the content between the commands 
    \\begin{document} and \\end{document}.'''

    @wraps(func)
    def decorated(obj, encoding='utf8', document=True, packages=None, required_packages=None, **kwds):
        if required_packages is None:
            required_packages = []

        out_data = func(obj, required_packages=required_packages, **kwds)
        out_data = out_data.encode(encoding)
        for p in required_packages:
            if p not in packages:
                packages.append(p)
        return render_tmpl_name('latex/document', packages=packages, document=out_data)

    #TODO: uniform latex API
    return func

latex.api = latex_api

@multimethod(anything)
def pdflatex(obj, **kwds):
    media = kwds.pop('media', {})
    tex = latex(obj, **kwds)
    pdffile = pdfcreate.pdflatex(tex.encode('utf8'), media=media)
    try:
        data = pdffile.read()
    finally:
        pdffile.close()
    return data

@multimethod(anything)
def pprint(obj, **kwds):
    return unicode(obj)

@multimethod(anything)
def xhtml(obj, **kwds):
    return unicode(obj)

RENDERERS = {'latex': latex, 'pprint': pprint, 'xhtml': xhtml,
             'pdflatex': pdflatex}

#===============================================================================
# Renderers for basic types
#===============================================================================
@pprint.dispatch(Renderer)
def pprint_renderer(obj, **kwds):
    if 'pprint' in obj.renderers():
        return obj.render('pprint', **kwds)
    else:
        return pprint[anything](obj)

@pprint.dispatch(basestring)
def pprint_str(obj, **kwds):
    return obj.decode(kwds.get('encoding', 'ascii'))

@pprint.dispatch(collections.Mapping)
def pprint_mapping(obj, **kwds):
    stream = ['{ ']
    for (k, v) in obj.items():
        stream.append(pprint(k, **kwds))
        stream.append(': ')
        stream.append(pprint(v, **kwds))
        stream.append(',\n  ')
    stream.pop()
    stream.append(' }')
    return ''.join(stream)

@pprint.dispatch(collections.Sequence)
def pprint_seq(obj, **kwds):
    stream = ['[']
    obj_print = [ pprint(x, **kwds) for x in obj ]
    size = sum(len(x) for x in obj_print)
    sep = (', ' if size < 40 else ',\n ')
    for pp in obj_print:
        stream.append(pp)
        stream.append(sep)
    stream.pop()
    stream.append(']')
    return ''.join(stream)

if __name__ == '__main__':
    print(render({'foo': 'bar', 'ham': ['spam', 'eggs', 'coffee']}))
    import doctest
    doctest.testmod()

