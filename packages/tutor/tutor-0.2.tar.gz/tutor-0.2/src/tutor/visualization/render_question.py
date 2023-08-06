from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.visualization' #@ReservedAssignment
    import tutor.visualization #@UnusedImport

from ..types import Question, QuestionPool
from .template import render_tmpl_name
from .render_base import pprint, latex

#===============================================================================
# Pretty printers
#===============================================================================
@pprint.dispatch(Question)
def pprint_question(qst, compact=False):
    if compact:
        lines = [qst.name.upper]
    else:
        lines = [qst.name, '-' * len(qst.name),
                 '  title: %s' % qst.title,
                 '  author: %s' % qst.author,
                 '  value: %s' % qst.value,
                 '  ctime: %s' % qst.ctime, ]
    for subq in qst:
        rendered = [ '    ' + l for l in  pprint(subq).splitlines() ]
        rendered[0] = '  * ' + rendered[0][4:]
        lines.extend(rendered)
    return '\n'.join(lines)

#===============================================================================
# LaTeX printers
#===============================================================================
@latex.dispatch(QuestionPool)
@latex.api
def latex_question_pool(obj, is_document=True, revision= -1, **kwds):
    '''Renders a question object to display its template and the multiple 
    versions rendered from this template.
    
    >>> q = QuestionPool('foo'); q.commit(5)
    >>> print(latex(q)) # doctest: +ELLIPSIS
    \documentclass[11pt,brazil,twoside]{article}
    ...
    \end{document}
    '''

    opts = {'is_document': is_document}

    # Gets template and preamble
    opts['preamble'] = obj.preamble
    opts.update(obj.history[revision]['template'])
    opts['revision_id'] = obj.history[revision].id
    opts['revision_ctime'] = obj.history[revision].ctime
    opts['body'] = map(latex, opts['body'])

    # Adds meta data
    opts.update(obj.dictview)
    opts['version'] = obj.version

    # Questions
    questions = sorted((int(k), v) for (k, v) in
                               obj.history[revision].items() if k.isdigit())
    opts['questions'] = [ [latex(x, is_document=False, **kwds) for x in v] for (k, v) in questions ]
    opts['num_questions'] = len(questions)

    for k in ['name', 'author', 'title']:
        if not opts[k]:
            del opts[k]


    return render_tmpl_name('latex:question/template', opts)

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)

