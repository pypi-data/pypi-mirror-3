#-*- coding: utf8 -*-
'''
Let us start creating a very simple exam

>>> from tutor.types import QuestionPool, ExamPool
>>> q1 = QuestionPool('foo.qst'); q2 = QuestionPool('foo.qst')
>>> q1.commit(5); q2.commit(5)
>>> exm = ExamPool('foobar')
>>> exm.add_question(q1);  exm.add_question(q2)
>>> exm.commit(5)
'''
from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor' #@ReservedAssignment
    import tutor #@UnusedImport

import os
import functools
import string
from decimal import Decimal
import fs.osfs
from simpleinput import Input
from .permanence import openpath, savepath
from .types.response import Response, Empty, RawScore, Unreadable, ResponsePool
from .types import MultipleChoice

class GradingError(ValueError):
    pass

class PhraseMatch(object):
    '''Represents a list of phrases that can be matched against sub-phrases. 
    '''
    def __init__(self, phrases, case=False):
        self.case = case
        phrases = [ self.adjust_case(p) for p in phrases ]
        self.phrases = set(phrases)
        self.words = {}
        for phrase in self.phrases:
            words = set(phrase.split())
            for word in words:
                phrases = self.words.setdefault(word, set())
                phrases.add(phrase)

    def matchf(self, word):
        '''Match full words on phrases'''

        try:
            return self.words[self.adjust_case(word)]
        except KeyError:
            return set()

    def matchp(self, word):
        '''Match partial words'''

        match = set()
        word = self.adjust_case(word)
        for p in self.phrases:
            if word in p:
                match.add(p)
        return match

    def add_phrase(self, phrase):
        '''Adds a new phrase to the list'''

        phrase = self.add_phrase(phrase, self.case)
        self.phrases.add(phrase)
        wds = set(phrase.split())
        for word in wds:
            phrs = self.words.setdefault(word, set())
            phrs.add(phrase)

    def adjust_case(self, phrase):
        '''Return a string with the proper case'''
        if self.case:
            return phrase
        else:
            return phrase.lower()


class Correction(object):
    '''Starts a correction job.
    
    Correction is based in a mini-language used to specify the student 
    responses and convert it in structures that can be accepted by the 
    `SubQuestion.score` method. Each SubQuestion type has its own sub-language
    that is described in the docstring for the ``step_sub_*`` methods.
    
    Each response is codified as Response object that stores the score given 
    to the question, its value, and possibly some additional information.
    '''
    def __init__(self, stream=''):
        self._stack = list(reversed(stream))
        self._consumed = []
        self.steppers = None
        self.results = []
        if type(self) == Correction:
            raise TypeError('Must initialize a subclass (e.g., ExamCorrection)')

    def clear(self):
        '''Clears correction job'''

        self._stack = []
        self._consumed = []
        self.steppers = None
        self.results = []

    def push(self, data):
        '''Pushes extra data to the character stream.'''

        self._stack.extend(reversed(data))

    def consume(self):
        '''Consumes all data in the character stream or until the stepper 
        actions is depleted.'''

        if self.steppers is None:
            raise ValueError('Correction Job is not properly initialized')

        stack = self._stack
        while stack:
            if not self.steppers:
                return

            stepper = self.steppers.pop()
            res = stepper()
            if res is not None:
                self.results.append(res)

    #===========================================================================
    # Parser steps: implements each step of Correction parser 
    #===========================================================================
    def genstep(func): #@NoSelf
        '''Transforms a function into a decorator that creates a step function
        to be appended to self.steps'''

        @functools.wraps(func)
        def decorator(self, *args, **kwds):
            def decorated():
                return func(self, *args, **kwds)
            return decorated

        return decorator

    @genstep
    def step_question(self, question):
        '''Processes a Question object. Question objects are not scored 
        directly, but through its sub-questions. 
        '''

        for subq in reversed(question.body):
            method_name = 'step_sub_' + type(subq).__name__.lower()
            method = getattr(self, method_name)
            self.steppers.append(method(subq))

    @genstep
    def step_sub_introtext(self, subq):
        '''IntroText objects are not scored, hence this method simply skips 
        them.'''

        return

    @genstep
    def step_sub_multiplechoice(self, subq):
        '''Mini-language to evaluate multiple-choice answers. 
        
        **Single answers**
          A single letter is expected and it is interpreted as a numerical index 
          of the chosen item: e.g., the letter 'a' is 0, 'b' is 1 and so on. Since
          the score object expects responses to be lists, these values are 
          converted into a single character list.
        
        **Multiple answers**
          Multiple answers are enclosed by parenthesis: e.g.: '(ab)' is 
          converted to the list [0, 1]
          
        **Empty**
          Empty responses are represented by an asterisk '*'.
          
        **Confusing/unreadable**
          Represented by an interrogation mark '?'.
          
        **Direct scoring**
          Scores can also be assigned directly by using a percentage number
          like '50%'.
        '''
        char = self._stack.pop().lower()

        # Not marked
        if char == '*':
            self._consumed.append(char)
            return Empty(subq)

        # Confusing/Unreadable marking
        elif char == '?':
            self._consumed.append(char)
            return Unreadable(subq)

        # Direct percentage score
        elif char.isdigit():
            chars = [char]
            while char.isdigit() or char == '.':
                try:
                    char = self._stack.pop()
                except IndexError:
                    # Empty _stack. Will raise a GradingError afterwards
                    # because char list does not end with a '%' sign. 
                    break
                chars.append(char)

            if chars[-1] != '%':
                raise GradingError('invalid percentage: %s' % ''.join(chars))
            num = ''.join(chars)
            self._consumed.extend(num)
            return RawScore(subq, Decimal(num[:-1]) / 100)

        # Group of markings
        elif char == '(':
            chars, char = [char], 'a'
            while char in string.ascii_letters:
                try:
                    char = self._stack.pop()
                except IndexError:
                    # Empty _stack. Will raise a GradingError afterwards
                    # because char list does not end with the closing paren
                    break
                chars.append(char.lower())
            if chars[-1] != ')':
                raise GradingError('invalid group: %s' % ''.join(chars))

            marked = chars[1:-1]
            valid = string.ascii_letters[:len(subq.items)]
            if any(c not in valid for c in marked):
                marked = ''.join(marked)
                raise GradingError("valid responses are in range 'a-%s', got: '%s'" % (valid[-1], marked))

            marked = (ord(c) - ord('a') for c in marked)
            resp = [ subq.order[n] for n in marked ]
            self._consumed.extend(chars)
            return Response(subq, data=dict(zip(resp, marked)))

        # Marked one letter
        else:
            num = ord(char) - ord('a')
            if num > len(subq.items):
                raise GradingError('invalid char: %s' % char)
            else:
                if subq.order:
                    try:
                        num = subq.order[num]
                    except IndexError: # answer larger question size
                        valid = string.ascii_letters[:len(subq.items)]
                        raise GradingError("valid responses are in range 'a-%s', got: '%s'" % (valid[-1], char))
                self._consumed.append(char)
                return Response(subq, data={num: char})

    del genstep

    # Properties ---------------------------------------------------------------
    @property
    def stream(self):
        return ''.join(reversed(self._stack))

    @property
    def consumed(self):
        return ''.join(self._consumed)

class ExamCorrection(Correction):
    def __init__(self, exam, stream=''):
        '''Initializes correction Job from an Exam object.'''

        super(ExamCorrection, self).__init__(stream)
        self.steppers = [ self.step_question(q) for q in reversed(exam.body) ]
        self.exam = exam

    def clear(self):
        super(ExamCorrection, self).clear()
        self.steppers = [ self.step_question(q) for q in reversed(self.exam.body) ]

    def score(self):
        '''Grades the exam up to the corrected questions'''

        #TODO: acabar com esse metodo em prol de exam.score(). Ele calcula o 
        # escore errado, de qualquer maneira. Permanece aqui somente para 
        # documentar o erro e corrigir o escore das provas antigas
        raise

        total = Decimal(0)
        grade = Decimal(0)
        for response in self.results:
            value, score = response.value, response.score
            total += value
            grade += score * value

        return grade / total * self.exam.value

    def report(self):
        '''Report the results of correction'''

        lines = []
        responses = list(self.results)
        strlens = set()
        values = []
        for qst in self.exam:
            for subq in qst.scoring:
                try:
                    response = responses.pop(0)
                except ValueError:
                    response = None

                assert subq.ref == response.objref
                aux = self._subqreport(subq, response)
                values.append([self.index(subq, fmt=True)] + list(aux))
                for x in aux:
                    strlens.add(len(x))

        padding = max(strlens) + 2
        for value in values:
            fmt, response, value, correct = (x.ljust(padding) for x in value)
            fmt = fmt.strip().rjust(padding)
            msg = '  %s) response: %s value: %s correct: %s'
            msg %= fmt, response, value, correct
            lines.append(msg)
        return '\n'.join(lines)

    def _subqreport(self, subq, response):
        if isinstance(subq, MultipleChoice):
            correct = subq.correct_idx
            correct = (subq.order.index(i) for i in correct)
            correct = ', '.join(string.ascii_lowercase[i] for i in correct)

        if isinstance(response, Empty):
            response, value = '---', '---'
        elif isinstance(response, RawScore):
            response, value = '---', '%s%%' % (response.score * 100)
        elif isinstance(subq, MultipleChoice):
            value = (subq.items[x].value * 100 for x in response.data)
            value = ', '.join('%s%%' % v for v in value)
            response = ', '.join(map(str, response.data.values()))

        return response, value, correct


    def consume_data(self, data):
        '''Adds data to stream and consume it'''

        self.push(data)
        self.consume()

    def index(self, subq=None, fmt=False, next=False):
        '''Return the index of the next question/subquestion that shall be
        corrected. If the question have a single non-display subquestion, the 
        index will be None'''

        if fmt:
            a, b = self.index(subq=subq, fmt=False, next=next)
            if b is None:
                return '%s' % (a + 1)
            else:
                return '%s.%s' % (a + 1, b + 1)

        if subq is None:
            if self.results:
                ref = self.results[-1].objref
                qst = self.exam.pool.question(ref[0])
                subq = qst.history[ref[1]][ref[2]][ref[3]]
            else:
                subq = self.exam[0].scoring[0]

            if next and not self.results:
                return (0, None) if len(subq.parent.scoring) == 1 else (0, 0)

        qst = subq.parent
        exam = qst.parent
        qst_idx = exam.index(qst)
        sub_idx = subq.question_index(scoring=True)

        if not next:
            if len(qst.scoring) > 1:
                return (qst_idx, sub_idx)
            else:
                return (qst_idx, None)
        else:
            try:
                # Check if there is a next sub-question
                qst.subquestion(sub_idx + 1, scoring=True)
                sub_idx += 1
                return (qst_idx, sub_idx)
            except:
                qst_idx += 1
                qst = exam[qst_idx]
                try:
                    # Check if there is a more then one scoring sub-questions
                    qst.subquestion(1, scoring=True)
                except ValueError:
                    return (qst_idx, None)
                else:
                    return (qst_idx, 0)

class iExamCorrection(ExamCorrection):
    '''A correction subclass that implements a interactive text-mode correction
    Job of a Exam object
    
    Examples
    --------
    
    >>> from tutor.examples import new_exam
    >>> corr = iExamCorrection(new_exam(3)[-1, 0], inputs=['100%', 'a*'])
    >>> corr.loop() #doctest: +ELLIPSIS
    Digite as respostas (exame ...-0)
        0%  1) 100%
      100%  2) a*
    <BLANKLINE>
    Nota final: *...%*
    1) response: ---      value: 100.0%   correct: ...
    2) response: a        value: ...       
    3) response: ---      value: ---      correct: ...  
    '''

    def __init__(self, exam, lang='en', stream='', inputs=None):
        super(iExamCorrection, self).__init__(exam, stream=stream)
        self.lang = lang
        self.input = Input(getinput=inputs)

    def loop(self):
        '''Executes the main correction loop and return the grading results'''

        print('Digite as respostas (exame %s-%s-%s)' %
              (self.exam.id, self.exam.revision_id, self.exam.revision_key))

        score = 0
        while self.steppers:
            if not self.stream:
                idx = self.index(fmt=True, next=True)
                data = self.input.str_input(('%i' % score).rjust(5) + '%% %s) ' % idx)
                self.push(data)
            else:
                break
            try:
                self.consume()
            except GradingError as ex:
                print('Erro: %s' % ex)
                if self.input.yn_input('\nRepetir correção? (S/n) ', yes='sim', no='não', default=True):
                    self.clear()
                else:
                    print()
                    break

        if self.stream:
            raise ValueError('Respostas adicionais: %s' % self.stream)

        self.response = self.exam.response(self.results)
        score = self.response.score

        print('\nNota final: *%i%%*' % score)
        print(self.report())

class iExamPoolCorrection(object):
    '''Interactive correction of a exam pool with students taken from a list.
    
    Examples
    --------
    
    >>> from tutor.examples import new_exam
    >>> students = ['João da Silva 0012423', 'Maria José 12132', 'José da Silva 0012342']
    >>> corr = iExamPoolCorrection(new_exam(3), students, inputs=['1', 'Foo', 'José', '1', '02', 'abc', 'Maria', '01', 'abcd', 's', 'abc', '', 's'])
    >>> corr.loop() #doctest: +ELLIPSIS
    Escolha a revisão: 
    ...
    Sair? (s/n) s
    '''

    def __init__(self, pool, students, inputs=None):
        self.pool = pool
        self.students = PhraseMatch(students)
        self.results = {}
        self.input = Input(getinput=inputs)

    def loop(self):
        revnames = [rev.id for rev in reversed(self.pool.history)]
        revnames[0] += ' (última)'
        idxs = reversed(range(len(self.pool.history)))
        revision = self.input.choice_input('Escolha a revisão: ', revnames, ret_choice=idxs, error_msg='{indent}inválido!')
        print('Revisão: **%s**\n' % self.pool.history[revision].id)
        self.revision = self.pool.history[revision].id

        while True:
            print('-----')
            stu = self.input.str_input('Nome/matrícula do(a) estudante: ')
            if not stu and self.input.yn_input('Sair? (S/n) ', yes='sim', no='não', default=True):
                break

            # Find student
            match = self.students.matchp(stu)
            if not match:
                print('*Não encontrado!* Digite novamente\n')
                continue
            elif len(match) == 1:
                stu = match.pop()
            else:
                match = sorted(match)
                match_disp = [ stu.title() for stu in match ]
                stu = self.input.choice_input('Escolha:', match_disp, ret_choice=match)
            print('Estudante: **%s**' % stu.title())

            # Find exam
            exm_idx = self.input.int_input('\n-----\nNúmero do exame: ')
            while True:
                exm_corr = iExamCorrection(self.pool[revision, exm_idx], inputs=self.input.getinput)
                try:
                    exm_corr.loop()
                except Exception as ex:
                    raise
                    print('Erro: %s' % ex)
                    if not self.input.yn_input('\nRepetir correção? (S/n) ', yes='sim', no='não', default=True):
                        print()
                        break
                    else:
                        print()
                else:
                    self.results[stu.encode('utf8')] = exm_corr.response
                    print()
                    break

class iExamFileCorrection(object):
    def __init__(self, exam_f=None, classroom_f=None, save_to=None, inputs=None):
        self.exam_f = exam_f
        self.classroom_f = classroom_f
        self.save_to = save_to
        self.input = Input(getinput=inputs)

    def getfiles(self, ext):
        '''Return a list with all files with the given extension'''

        base = fs.osfs.OSFS('')
        files = base.listdir()
        lower = sorted(f for f in files if f.endswith(ext))
        upper = []
        base, _ = os.path.split(base.getsyspath(''))
        base, _ = os.path.split(base)
        depth = 0
        while base != '/':
            depth += 1
            upper.extend(sorted('../' * depth + f for f in os.listdir(base) if f.endswith(ext)))
            base, _ = os.path.split(base)

        return lower + upper

    def loop(self):
        if self.classroom_f is None:
            cfiles = self.getfiles('.cls')
            if not cfiles:
                print('error: no classroom files found!')
                return
            cfile = self.input.choice_input('-----\nChoose classroom file:', cfiles)
            print()
        else:
            cfile = self.classroom_f

        if self.exam_f is None:
            efiles = self.getfiles('.exm')
            if not efiles:
                print('error: no exam files found!')
                return
            efile = self.input.choice_input('-----\nChoose exam file:', efiles)
            print()
        else:
            efile = self.exam_f

        exam = openpath(efile)
        classroom = openpath(cfile)
        students = ['{full_name}---{id}'.format(**std.dictview) for std in classroom.students ]
        corr = iExamPoolCorrection(exam, students, self.input.getinput)
        try:
            corr.loop()
        finally:
            results = self.results = dict(corr.results)

            rpath = efile[:-4] + '.resps'
            if os.path.exists(rpath):
                with open(rpath) as data:
                    data = data.read()
                with open(rpath + '~', 'w') as F:
                    F.write(data)
                respspool = openpath(rpath)
            else:
                respspool = ResponsePool(exam.id, corr.revision)
            for resp in results.values():
                respspool.addresponse(resp)
            savepath(respspool, rpath)

if __name__ == '__main__':
    import os
    os.chdir('_trash')
    iExamFileCorrection(inputs=['2', '1', '1', 'João', '12', 'abcdefg', '', 'ab', '', 'abcde', '', '']).loop()

#    import doctest
#    doctest.testmod()
