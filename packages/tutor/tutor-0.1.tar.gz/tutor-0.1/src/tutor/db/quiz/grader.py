#-*- coding: utf8 -*-
from __future__ import print_function
from future_builtins import *
from tutor.quiz import *
from tutor.question import *
import pprint

QROMAN = 'I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX XXI XXII XXIII XXIV XXV XXVI XVII XVIII XXIX XXX'.split()

def igrade(quiz, answers='', disp=True, disp_ok=False, barcode=None, value=10.):
    """
    Compute the grade interactively
    
    Input
    -----
    
    @param quiz: quiz or template to be graded
    @param answers: a string representing the answers marked by the student
    @param disp: show 
    @param disp_ok:
    @param barcode:
    @param value:
    """
    # if quiz is a template, creates a dummy quiz and assign to it the right 
    # seed in order to proceed
    if isinstance(quiz, QuizT):
        quiz = Quiz.load(quiz, recycle=1)
        try:
            old_seed = quiz.seed

            if barcode is None:
                barcode = raw_input('\nBarcode: ')
                raw_input() #TODO: find a better way to solve the CE LF problem in Linux
                if not barcode:
                    print('*Skipped test*')
                    return 0
                barcode = int(barcode)
            quiz.seed = barcode
            return igrade(quiz, answers)

        finally:
            quiz.seed = old_seed

    # answers from quiz
    q_answers = quiz.answers
    score = 0.0
    max_score = 0.0
    marked_answers = []

    for qn, question in enumerate(quiz.questions):
        q_value, q_answer = q_answers[qn]
        for nn, node in enumerate(question.question_nodes):
            max_grade, good_ans = q_answer[nn]
            code = '%s.%s' % (qn + 1, QROMAN[nn])
            if nn == 0 and len(question.question_nodes) == 1:
                code = str(qn + 1)

            # try to extract the next answer or ask the user to type
            # it into the cli.
            try:
                (grade, marked), answers = node.read_answers(answers, code)
            except ValueError:
                while True:
                    try:
                        print('Invalid answer to q %s' % code)
                        (grade, marked), answers = node.read_answers('', code)
                        break
                    except:
                        continue

            # display the wrong/right answers
            if disp:
                ans_h = node.fmt_answer(marked)
                rans_h = node.fmt_answer(good_ans)
                grade_p = int(100. * grade / max_grade)
                if marked is None:
                    print('  - %s *skipped*, should be (%s)' % (code.ljust(5), rans_h))
                elif marked != good_ans:
                    print('  - %s got (%s), answer is (%s) --- (%s%%)' % (code.ljust(5), ans_h, rans_h, grade_p))
                elif disp_ok:
                    print('  - %s answer is OK' % code.ljust(5))

            # save grade
            a = node.fmt_answer(marked)
            marked_answers.append(a if a else ' ')
            score += grade * q_value * node.grade
            try:
                max_score += node.fixed_grade * q_value
            except:
                max_score += max_grade * q_value

    # compute maximum score
    score = score / max_score * value

    if disp:
        answers = ''.join(marked_answers)
        print("Barcode: %s, answers: '%s'" % (quiz.seed, answers))
        print('Score: %s out of %s' % (score, value))
    return score

if __name__ == '__main__':
    try:
        qt = QuizT.load('lista5-c3')
    except:
        qt = QuizT(name='lista5-c3',
                   title=u'Quinta prova optativa de Cálculo 3',
                   teacher=u'Fábio Mendes e Marcelo de Carvalho')
        qt.add_question('c3/integrais_linha/forcas_conservativas')
        qt.add_question('c3/integrais_linha/centroide_semicirculo')
        qt.add_question('c3/integrais_linha/conceituais')
        qt.add_question('c3/integrais_linha/trabalho_balistico')
        qt.add_question('c3/integrais_linha/helicoidal')
        qt.add_question('c3/integrais_linha/inercia_linha')
        qt.save()

#    seed = 679662
#    ans = 'dadbeaaa'
#    seed = 873289
#    ans = 'adcbdabz'
    seed = 762964
    st1 = 'c3/integrais_linha/forcas_conservativas'
    st2 = 'c3\/integrais_linha\/forcas_conservativas'
    #seed = seed - hash(st1) + hash(st2)
    seed = seed + hash(st1)
    ans = 'abbabbb'
    #qt.nullify_question(4, 0, assign_grade=False)
    q = qt.new_quiz()
    qt.nullify_question(1, assign_grade=True)
    qt.nullify_question(2, assign_grade=False)
    qt.nullify_question(3, assign_grade=True)
    qt.nullify_question(4, assign_grade=True)
    qt.nullify_question(5, assign_grade=True)
    qt.questions[2].grade = 0
    qt.save()
    grades = {}

    for seed in xrange(1000000):
        ans = 'abbabbb                                                   '
        q.seed = seed
        grade = grades[seed] = igrade(q, ans, barcode=seed, disp=False)
        if grade >= 1.66:
            print('grade: %s, seed: %s' % (grade, seed))
