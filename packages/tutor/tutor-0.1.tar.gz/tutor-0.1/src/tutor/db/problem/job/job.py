#-*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from future_builtins import *
from tutor.quiz import QuizT

class Job(object):
    def __init__(self, quiz_t, N, disp=False):
        self.template = quiz_t
        self.N = N
        f = lambda i: print("Creating quiz %s..." % (i+1))
        self.quizzes = [ (quiz_t.new_quiz(), f(i))[0] for i in range(N) ]
                
    def source(self, **kwds):
        source = [ q.source(**kwds) for q in self.quizzes ]
        source = '\n\n\\cleardoublepage{}\n\n'.join(source)
        source = u'''\\documentclass[11pt,brazil,twoside]{article}
\\usepackage[T1]{fontenc}
\\usepackage[utf8]{inputenc}
\\usepackage[a4paper]{geometry}
\\geometry{verbose,tmargin=2cm,bmargin=2cm,lmargin=1.5cm,rmargin=1.5cm}
\\usepackage{amsmath}
\\usepackage{graphicx}
\\usepackage{babel}
\\usepackage{auto-pst-pdf,pst-barcode,pstricks-add}

\\def\\multiplechoice {}
\\def\\intro {}

\\begin{document}

%s

\\end{document}
 ''' % source
        return source
    
    def make_latex(self, fpath):
        pass
    
    def make_pdf(self, fpath):
        pass
    
if __name__ == '__main__':
    qt = QuizT(title = u'Teste',
               teacher = u'Fábio Mendes')
    qt.add_question('exemplos/demo')
    qt.add_question('exemplos/demolyx')
    qt_prova = qt
    qt.save()
    
    j = Job(qt, 5, disp=True)
    #j = Job(qt, 65, disp=True)
    with open('/home/chips/tmp/job.tex', 'w') as F:
        src = j.source(toprint=True).encode('utf8')
        print(src)
        F.write(src)