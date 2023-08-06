from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.visualization' #@ReservedAssignment
    import tutor.visualization #@UnusedImport
#-------------------------------------------------------------------------------

from datetime import date, datetime
from ..util.multimethod import multimethod, anything

FILTERS_USER = FILTERS_LATEX = {}
FILTERS_PPRINT = {}
FILTERS = {
    'latex': FILTERS_LATEX,
    'user': FILTERS_USER,
    'pprint': FILTERS_PPRINT,
}

def is_filter(*args):
    '''Decorates a function to be a filter of the given types'''
    if args == ('all',):
        args = 'latex', 'user', 'pprint'

    def decorator(func):
        for arg in args:
            FILTERS[arg][func.__name__] = func
        return func
    return decorator

@is_filter('all')
def render(obj, renderer=None):
    '''Filter that calls obj.render() or returns its string representation.
    
    If given, the optional argument ``renderer`` is passed to the render() 
    method.
    '''

    try:
        render_func = obj.render
    except AttributeError:
        return unicode(obj)
    else:
        if renderer is None:
            return render_func()
        else:
            return render_func(renderer)

@is_filter('all')
def render_from_template(obj, template, env='latex'):
    '''Renders an object using the given template.'''

    from .template import render_tmpl_name
    template = '%s:%s' % (env, template)
    return render_tmpl_name(template, obj)

@is_filter('all')
def render_from_type(obj, env='latex', append=''):
    '''Renders an object choosing a template based on its type key.'''

    from .template import render_tmpl_name
    append = '.' + append if append else append
    try:
        template = obj['type']
    except (KeyError, TypeError):
        template = obj.type

    # strip the "tutor-" part from the beginning of the name 
    template = template[6:]
    template = template.replace(':', '/')
    template = '%s:%s%s' % (env, template, append)
    return render_tmpl_name(template, obj)

@is_filter('all')
def finalize(obj):
    return unicode(obj)

#===============================================================================
# LaTeX filters
#===============================================================================
@is_filter('latex')
def opt_args(obj, braces=True):
    '''Renders a dictionary as string representing optional LaTeX arguments.
    
    Examples
    --------
    
    >>> opt_args({'a': True, 'b': 'c'})
    u'[a, b=c]'
    '''

    if obj:
        result = ['[']
        for k, v in obj.items():
            if v == True:
                result.append(unicode(k))
            else:
                result.append(u'%s=%s' % (k, v))
            result.append(', ')
        result[-1] = ']'
        return ''.join(result)
    else:
        return ''

BRACE_PAIRS = dict(u'() [] {} <>'.split())
BRACE_PAIRS.update((v, k) for (k, v) in BRACE_PAIRS.items())

@is_filter('latex')
def braces(obj, brace='{'):
    '''Enclose string in braces. (Uses curly braces as default)

    Examples
    --------
    
    >>> braces('a')
    u'{a}'
    >>> braces('a', '<<')
    u'<<a>>'
    '''
    if len(brace) > 1:
        out, rest = brace[0], brace[1:]
        return braces(braces(obj, rest), out)

    closing_brace = BRACE_PAIRS.get(brace, brace)
    return u''.join([brace, obj, closing_brace])

@is_filter('latex')
def unplastex(obj):
    '''Attempt to correct a few small bugs in PlasTeX manipulated source'''
    return obj.replace('\\{ ', '\\{')

@is_filter('latex')
def safetex(obj):
    '''Safe latex strings'''
    return obj.replace('_', '\\_')

@is_filter('latex')
def finalize(obj): #@DuplicatedSignature
    return tex_finalize(obj)

@multimethod(anything)
def tex_finalize(obj): #@DuplicatedSignature
    return unicode(obj)

@tex_finalize.dispatch(datetime)
def tex_finalize(obj):
    return u'%s/%s/%s %s:%s' % (obj.day, obj.month, obj.year, obj.hour, obj.minute)

@tex_finalize.dispatch(date)
def tex_finalize(obj):
    return u'%s/%s/%s' % (obj.day, obj.month, obj.year)

@tex_finalize.dispatch(tuple)
def tex_finalize(obj):
    return u'(%s)' % (u','.join(finalize(x) for x in obj))

@tex_finalize.dispatch(list)
def tex_finalize(obj):
    return u'[%s]' % (u','.join(finalize(x) for x in obj))

#===============================================================================
# Pprint fiters
#===============================================================================

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
