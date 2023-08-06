from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.visualization' #@ReservedAssignment
    import tutor.visualization #@UnusedImport

from ..types.subquestions import IntroText, MultipleChoice
from .template import render_tmpl_name
from .render_base import pprint, latex

#===============================================================================
# IntroText
#===============================================================================
@pprint.dispatch(IntroText)
def pprint_introtext(obj, required_packages=None, **kwds):
    text = obj.text
    return (text if len(text) < 60 else text[:57] + '...')

@latex.dispatch(IntroText)
@latex.api
def latex_introtext(obj, required_packages=None, **kwds):
    return render_tmpl_name('latex:question/intro', obj._data)

#===============================================================================
# MultipleChoice
#===============================================================================
@pprint.dispatch(MultipleChoice)
def pprint_multiplechoice(obj, required_packages=None, **kwds):
    lines = [(obj.stem if len(obj.stem) < 60 else obj.stem[:57] + '...')]
    lines.append('value: %s' % obj.value)
    lines.append('order: %s' % obj.order)
    lines.append('multiple answers: %s' % obj.multiple_answers)
    for item in obj.items:
        lines.append('* (%s) %s' % (item.value, item.text))
    return '\n'.join(lines)


@latex.dispatch(MultipleChoice)
@latex.api
def latex_multiplechoice(obj, required_packages=None, mark_correct=True, **kwds):
    opts = {}
    if obj.order:
        items = opts['items'] = [ obj.items[k] for k in obj.order ]
    else:
        items = obj.items

    if obj.columns > 1:
        opts['items'] = []

        # Create table_header
        size = (0.9 - obj.columns / 45.) / obj.columns
        col_header = '>{\\raggedright}p{%.3f\\textwidth}' % size
        header = '{%s}' % (col_header * obj.columns)

        # Create table_rows
        letters = list('abcdefghijklmnopqrstuvwxyz')
        elems = items[:]
        rows = []

        # Create each row
        N, Nc = len(items), max(obj.columns, 1)
        N_rows = N / Nc + int(bool(N % Nc))

        for _ in range(int(N_rows)):
            cols = []
            for _ in range(Nc):
                try:
                    elem = elems.pop(0)
                    text = elem.text.strip()
                    letter = '%s) ' % letters.pop(0)
                except IndexError:
                    text = ''
                    letter = ''
                if text == '$$':
                    text = '$~$'
                if mark_correct and elem.iscorrect():
                    letter = '\\textcolor{red}{\\bf %s}' % letter
                cols.append(letter + text)
            rows.append(' & '.join(cols))

        opts['render_items'] = True
        opts['table_header'] = header
        opts['table_rows'] = rows

    return render_tmpl_name('latex:question/multiple-choice', obj._data, opts)

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)
