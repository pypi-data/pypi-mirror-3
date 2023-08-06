#-*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from future_builtins import *
import string
import json
import hashlib
from tutor.config import schemas
from tutor.lib.loaders import exam as loaders
from tutor.db.base import ORMModel, HasChildren, models
from tutor.db.learning_obj import LearningObj
from tutor.db import nodes

__all__ = [ 'Exam' ]

class Exam(ORMModel, HasChildren):
    schema = schemas.Exam
    db_fields = [ 'name', 'is_template', 'template_name', 'title', 'parent' ]
    db_fields_init = { 'parent': { 'null': True } }
    related_lobjs = models.ManyToManyField(LearningObj, null=True)

    @classmethod
    def from_keys(cls, *args, **kwds):
        new = super(Exam, cls).from_keys(*args, **kwds)
        list(new._iter_content())
        new.pre_save()
        new.save()
        return new

    def child(self, **kwds):
        child = super(Exam, self).child(**kwds)

        # Update content
        for i, lobj in enumerate(self.content):
            if '::' not in lobj.name:
                lobj = lobj.child()
            child.related_lobjs.add(lobj)
            child._json['content'][i] = lobj.name

        child.pre_save()
        child.save()
        return child

    def pretty(self, **kwds):
        kwds['parent'] = "'%s'" % self.parent_id
        kwds['content'] = self._json['content']
        return super(Exam, self).pretty(**kwds)

    def answers_box(self, list=None):
        if list is None:
            idx = 0
            list = []
            for lobj in self.content:
                idx += 1
                for node in lobj.content:
                    if isinstance(node, nodes.HasAnswers):
                        list.append(idx)
        
        letters = string.ascii_lowercase
        list_fmt = []
        last, rep_idx = None, 0
        for x in list:
            if x == last:
                if rep_idx == 0:
                    list_fmt[-1] = '%s.a' % x
                rep_idx += 1
                list_fmt.append('%s.%s' % (x, letters[rep_idx]))
            else:
                last, rep_idx = None, 0
                list_fmt.append('~%s~' % x)
            last = x
        
        head = '|%s|' % ('|'.join('c' for x in list_fmt))
        line1 = ' & '.join(list_fmt)
        line2 = ' & '.join('' for x in list_fmt)
        
        return ur'''\begin{center}
\textbf{Respostas}\\
\begin{tabular}{%(head)s}
\hline 
%(line1)s\tabularnewline
\hline 
\hline 
%(line2)s\tabularnewline
\hline 
\end{tabular}

%%s
\end{center}''' % { 'head': head, 'line1': line1, 'line2': line2 }

    @property
    def barcode_st(self):
        return self.barcode()

    def barcode(self, data=None, amplify=False, center=False):
        """LaTeX source that creates a barcode with text 'data'"""

        # fix data
        if data is None:
            data = self.name.split('::')[-1]

        # seed to reconstruct answers
        if amplify:
            scalex = scaley = '1.3' if amplify == True else str(float(amplify))
        else:
            scalex = scaley = '0.9'

        # latex code
        code = u'\\psbarcode[scalex=%s,scaley=%s]{^104%s}'\
               u'{includetext guardwhitespace height=0.9}{code128}' % (scalex, scaley, data)
        code = u'\\psset{unit=1in}\n\\begin{pspicture}(3.5,1.2)\n%s\n\\end{pspicture}' % code
        if center:
            code = u'\\begin{center}\n%s\n\\end{center}' % code

        return self.answers_box() % code

    # Properties transformations -----------------------------------------------
    def _iter_content(self, names=None):
        if names is None:
            names = self._json['content']
        for name in names:
            try:
                yield self.related_lobjs.get(name=name)
            except LearningObj.DoesNotExist:
                lobj = LearningObj.from_lib(name, try_pk=True)
                self.related_lobjs.add(lobj)
                yield lobj

    def T_content_object(self, json):
        return list(self._iter_content(json))

    def T_content_json(self, obj):
        names = set(obj)

        for item in self.related_lobjs:
            if item.name not in names:
                self.related_lobjs.delete(item)

        ret_value = []
        for item in obj:
            ret_value.append(unicode(item.name))
            self.related_lobjs.add(item)

        return [ unicode(item.name) for item in obj ]

class Foo:
    def new_job(self, N, name=None, disp=0, **kwds):
        """Creates a new job that prints N different quizzes from template"""

        # if that is not taken care of, choose a new name for job
        if name is None:
            idx = 0
            name = self.name + '_%s' % idx
            names_taken = [ j.name for j in self.job_set.all() ]

            while name in names_taken:
                idx += 1
                name = self.name + '_%s' % idx

        # create the quizzes 
        quizzes = [ self.new_quiz(disp=i + 1, **kwds) for i in range(N) ]

        # creates job
        job = Job(name=name, template=self, N=N)
        job.save()
        for quiz in quizzes:
            job.quizzes.add(quiz)

        return job

    def compute_grade(self, answer_dict, seed, full_output=False):
        """
        
        @param answer_dict:
        @param full_output:
        @param seed: (int) seed for test
        """

        # creates a dummy Quiz object
        quiz = Quiz(template=self, seed=seed)
        quiz.save()
        try:
            for q in self.question_names:
                q = Question.load(q, recycle=1)
                quiz.raw_questions.add(q)
            grade = quiz.compute_grade(answer_dict, full_output)
        finally:
            quiz.delete()
        return grade

    def nullify_question(self, question, section=None, assign_grade=False):
        try:
            question.nullify(section, assign_grade)
        except AttributeError:
            idx = question
            self.questions[idx].nullify(section, assign_grade)

    # -- properties ------------------------------------------------------------
    @property
    def question_names(self):
        return [ name for (name, _value_) in self.question_list ]

    # -- methods ---------------------------------------------------------------
    @staticmethod
    def load_exam(addr):
        """
        Return a Quiz of the given 'template'. 
        
        Input
        -----
        
        @param template: (QuizT or string-like) template for given Quiz
        
        @param recycle: (int) if 0, always creates a new Quiz. If greater than 
            zero, it reuses an existing Quiz if the set of quizzes from the given 
            template has at least 'recycle' members.
        """
        if isinstance(template, basestring):
            template = QuizT.load(template)

        if recycle:
            questions = list(template.quiz_set.all())
            if len(questions) > recycle:
                return random.choice(questions)

        return template.new_quiz()

    def compute_grade(self, answer_dict, full_output=False):
        """
        
        @param answer_dict:
        @param full_output:
        """

        full_out = {}
        for n, question in enumerate(self.questions):
            ans = answer_dict.get(n, {})
            full_out[n] = question.compute_grade(ans, full_output=True)
        return full_out

#===============================================================================
#                                 Job
#===============================================================================
class Job():
    # -- other methods --------------------------------------------------------
    def source(self, **kwds):

        # try to retrieve source from cache
        try:
            if self._source_cache[0] == kwds:
                return self._source_cache[1]
        except AttributeError:
            pass

        tex = [ q.source(**kwds) for q in self.quizzes.all() ]
        tex = '\n\n\\cleardoublepage{}\n\n'.join(tex)
        tex = u'\\documentclass[11pt,brazil,twoside]{article}\n'\
               '\\usepackage[T1]{fontenc}\n'\
               '\\usepackage[utf8]{inputenc}\n'\
               '\\usepackage[a4paper]{geometry}'\
               '\\geometry{verbose,tmargin=2cm,bmargin=2cm,lmargin=1.5cm,rmargin=1.5cm}\n'\
               '\\usepackage{amsmath}\n'\
               '\\usepackage{graphicx}\n'\
               '\\usepackage{babel}\n'\
               '\\usepackage{esint}\n'\
               '\\usepackage{auto-pst-pdf,pst-barcode,pstricks-add}\n\n'\
               '\\def\\multiplechoice {}\n\\def\\intro {}\n'\
               '\\begin{document}\n\n%s\n\n\\end{document}' % tex

        # save source on cache
        self._source_cache = (kwds, tex)

        return tex

    def __unicode__(self):
        return '<Exam %s>' % repr(self.name)

    __str__ = __repr__ = __unicode__

#===============================================================================
# garbage...
#===============================================================================
if __name__ == '__main__':
#    import doctest
#    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)

#    LearningObj.objects.all().delete()
#    Exam.objects.all().delete()
#    e = Exam.from_lib('cálculo 3/módulo 1/lista')

#    e = Exam.from_lib('examples/simple_exam')
#    Exam.objects.all().delete()
#    LearningObj.objects.filter(name__startswith='cálculo 3/integrais múltiplas/inverter ordem parábola').delete()
#    LearningObj.objects.get(name='cálculo 3/derivadas parciais/diferencial total/aplicação 4').delete()
    LearningObj.objects.filter(name__startswith='cálculo 3/integrais múltiplas/área entre curvas').delete()
    for q in \
'''cálculo 3/integrais múltiplas/integral simples
cálculo 3/integrais múltiplas/área entre curvas
cálculo 3/integrais múltiplas/área entre sin cos
cálculo 3/integrais múltiplas/função gama
cálculo 3/integrais múltiplas/inverter ordem
cálculo 3/integrais múltiplas/inverter ordem parábola
cálculo 3/integrais múltiplas/conv polar
cálculo 3/integrais múltiplas/inércia
cálculo 3/integrais múltiplas/inércia disco
cálculo 3/integrais múltiplas/inércia triângulo'''.splitlines():
        LearningObj.objects.filter(name__startswith=q).delete()
        pass

    et = Exam.from_lib('cálculo 3/módulo 3/lista')
    e = et.child()
    e.pprint()
    e.save_pdf()
    
    with open('provas.tex', 'a') as F:
        i = 0
        while i < 80:
            try:
                e = et.child()
            except:
                continue
            else:
                i += 1
                F.write('\n\n\\cleardoublepage{}\n\n')
                F.write(e.latex(barcode=True))
                F.flush()
                e.save_pdf(barcode=True)
