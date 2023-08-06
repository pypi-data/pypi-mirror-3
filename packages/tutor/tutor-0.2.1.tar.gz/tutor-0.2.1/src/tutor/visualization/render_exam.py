from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.visualization' #@ReservedAssignment
    import tutor.visualization #@UnusedImport

import pyson
from ..types import Exam, ExamPool
from .template import render_tmpl_name
from .render_base import pprint, latex

#===============================================================================
# Pretty-print printers
#===============================================================================
@pprint.dispatch(Exam)
def pprint_exam(obj):
    lines = ['%s\n%s' % (obj.name, '-' * len(obj.name))]
    lines.append('title: %s' % obj.title)
    lines.append('author: %s' % obj.author)
    lines.append('value: %s' % obj.value)
    lines.append('ctime: %s' % obj.ctime)
    for item in obj:
        rendered = [ '    ' + l for l in  pprint(item).splitlines() ]
        rendered[0] = '  * ' + rendered[0][4:]
        lines.extend(rendered)
    return '\n  '.join(lines)

#===============================================================================
# LaTeX printers
#===============================================================================
@latex.dispatch(ExamPool)
@latex.api
def latex_exam_pool(obj, is_document=True, revision= -1, qnames=[], **kwds):
    '''Renders a exam object to its final print.
    
    >>> q1 = QuestionPool('foo'); q1.commit(5)
    >>> q2 = QuestionPool('bar'); q2.commit(5)
    >>> q3 = QuestionPool('foobar'); q3.commit(5)
    >>> exam = ExamPool('foo', title='My Exam')
    >>> exam.add_question(q1, q2, q3); exam.commit(10)
    >>> print(latex(exam)) # doctest: +ELLIPSIS
    \documentclass[11pt,brazil,twoside]{article}
    ...
    \end{document}
    '''

    opts = {'is_document': False}

    # Gets template and preamble
    questions = obj.questions
    preambles = (pyson.deepcopy(q.preamble(revision)) for q in questions)
    preamble = next(preambles)
    for p in preambles:
        preamble.update(p)
    opts['preamble'] = preamble

    # Adds meta data
    opts.update(obj.dictview)

    # ExamPool template
    exams = []
    revision = obj.history[revision]
    template = revision['template']
    for exam_no in revision.keys(True):
        if exam_no[0].isdigit():
            q_revs = (q.history[q_rev] for (q, (q_id, q_rev)) in zip(questions, template))
            q_bodies = [ q_rev[key] for (key, q_rev) in zip(revision[str(exam_no)], q_revs) ]
            rendquestions = ['\n\n'.join([latex(b, **kwds) for b in body]) for body in q_bodies]
            if qnames:
                rendquestions = ['{\\textit (%s)}%s' % (qname, q) for (qname, q) in zip(qnames, questions)]

            exams.append(render_tmpl_name('latex:exam', opts, questions=rendquestions, revision=revision, exam_no=exam_no))

    exams = '\n\\newpage{}\n'.join(exams)
    opts['is_document'] = is_document
    return render_tmpl_name('latex:document', opts, document=exams)

if __name__ == '__main__':
    from ..types import QuestionPool, ExamPool
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
