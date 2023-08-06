'''
Functions for creating examples of tutor objects to be used in tests or in the
tutor command line tool.
'''
from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.examples' #@ReservedAssignment
    import tutor.examples #@UnusedImport

import random
import fs.osfs
from ..latex.commands import lyxtotex
from ..types import QuestionPool, ExamPool
from ..paths import SYSTEM_EXAMPLES_DIR
examples = fs.osfs.OSFS(SYSTEM_EXAMPLES_DIR)

def new_subquestion(grading=True):
    '''Creates a new random subquestion object'''
    pass

def new_question(commit=10):
    '''New question.'''

    qnames = ['simple']
    qtypes = ['tex', 'lyx']
    random.shuffle(qnames)
    random.shuffle(qtypes)
    new = question_from_database(qnames[0], qtypes[0])
    new.commit(10)
    return new

def new_exam(nquestions=3, commit=10):
    exam = ExamPool('example', title='Example exam')
    for _ in range(nquestions):
        exam.add_question(new_question())
    if commit:
        exam.commit(commit)
    return exam

def from_database(tt, name, **kwds):
    '''sadsa'''

    return globals()[tt + '_from_database'](name, **kwds)

def question_from_database(name, qtype='tex'):
    qst = examples.opendir('questions/%s-src' % name)
    with qst.open('main.lyx') as F:
        if qtype == 'tex':
            F = lyxtotex(F)
        main = F.read().encode('utf8')
    with qst.open('namespace.py') as F:
        namespace = F.read()
    return QuestionPool('example', main_data=main, main_t=qtype, namespace_data=namespace)

if __name__ == '__main__':
    from tutor.visualization import latex
    print(latex(new_exam()))
