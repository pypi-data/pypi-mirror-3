'''
This module defines the Jinja2 environment used in ``Py-Tutor``. The default
syntax is not used in user templates because it would produce invalid LaTeX.
The system templates (e.g., ones used to render questions and exams) uses
the standard syntax.
 
The main reason for this split is that user templates files should always be
compilable LaTeX so we don't need to implement a full blown LaTeX parser in 
order to catch and report the errors in user's files.

'''

from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.visualization' #@ReservedAssignment
    import tutor.visualization #@UnusedImport

from .filters import FILTERS
from jinja2 import Environment, FileSystemLoader

__all__ = [b'get_environment', b'get_template', b'render_tmpl_name', b'render_template']

#===============================================================================
# Global environments 
#===============================================================================
LATEX_ENVIRONMENT = None
PPRINT_ENVIRONMENT = None
USER_ENVIRONMENT = None
ENV_KWARGS = {
    'latex': {},
    'pprint': {},
    'user': {
        'block_start_string': '<@',
        'block_end_string': '@>',
        'variable_start_string': '||',
        'variable_end_string': '||',
        'comment_start_string': '<!',
        'comment_end_string': '!>',
        'line_statement_prefix': '@!',
        'line_comment_prefix': '%%',
    }
}

#===============================================================================
# Environment loaders
#===============================================================================
def get_environment(env_name='user'):
    '''Returns a environment of the given ``env_name``. 
    
    Supported types are "default", "latex" and "pprint".
    
    Examples
    --------
    
    >>> env = get_environment()
    >>> t = env.from_string('foo says: ||bar||')
    >>> print(t.render(bar='bar is good!'))
    foo says: bar is good!
    '''
    import tutor.paths

    global_name = env_name.upper() + '_ENVIRONMENT'
    global_vars = globals()

    # Tries to load global variable
    try:
        env = global_vars[global_name]
        if env is not None:
            return env
    except KeyError:
        raise ValueError('unsupported environment type: %s' % env_name)

    # Get filters
    filters = dict(FILTERS[env_name])
    finalize = filters.pop('finalize')

    # Creates environment
    kwds = ENV_KWARGS[env_name]
    path = tutor.paths.SYSTEM_TEMPLATES_DIR
    loader = FileSystemLoader(path)
    env = Environment(finalize=finalize, autoescape=False, loader=loader, **kwds)
    global_vars[global_name] = env

    # Update filters, tests and globals
    env.filters.update(filters)
#    env.tests[]
#    env.globals[]
    return env

#===============================================================================
# Get template
#===============================================================================
def get_template(name):
    '''Returns the template from its name. Template names are strings of the 
    form "namespace:path/to/template", in which namespace can be any of the 
    supported environments ('default', 'latex', or 'pprint').
    
    Examples
    --------
    
    >>> get_template('latex:question/index')
    <Template u'question/index.latex.txt'>
    '''

    namespace, _, name = name.partition(':')
    if not namespace:
        raise ValueError('must provide namespace, got %s' % repr(name))
    env = get_environment(namespace)
    name = '%s.%s.txt' % (name, namespace)
    return env.get_template(name)

#===============================================================================
# Global rendering function
#===============================================================================
def render_tmpl_name(template_name, *args, **kwds):
    '''Renders arguments using the template identified by 'template_name'.
    
    Parameters
    -----------
    template_name : str
        A name identifying the template. It is formed as "type:address", in 
        which type can be "default", "latex", or "pprint" and is used to choose
        the environment used to load the template.
    args, kwds : dict-like
        Each element in args are a mapping of (name: value) with the values of 
        variables to be substituted into the template. The additional key=value
        keyword arguments are appended to the final dictionary.
        
    Examples
    --------
    
    >>> some_question = {
    ...     'title': 'Some title',
    ...     'name': 'some_question',
    ...     'author': 'some author',
    ...     'creation_date': 'some day',
    ...     'body': []}
    >>> print(render_tmpl_name('latex:question/index', some_question))
    %%------------------------------------------------------------------------------
    %% Question: some_question
    %%   - Title: Some title
    %%   - Creation: some day
    %%   - Version: 
    <BLANKLINE>
    %% End of question 'some_question'
    %%------------------------------------------------------------------------------
    '''

    namespace = {}
    for arg in args:
        namespace.update(arg)
    namespace.update(kwds)
    template_name = get_template(template_name)
    return template_name.render(namespace)

def render_template(data, method, *args, **kwds):
    '''
    Renders template
    '''
    if method == 'latex':
        env = get_environment('user')
    else:
        raise ValueError('unsupported method, %s' % repr(method))
    return env.from_string(data).render(*args, **kwds)

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
