#-*- coding: utf8 -*-
from grading import Grader
import simplejson
import os

inpt = raw_input('(L)ista ou (P)rova? ').lower()
if  inpt == 'p':
    basepath = '../bin/m1/p1-%s.json'
    graded = '../bin/m1/graded-%s.json'
    gp = Grader()

    while True:
        try:
            name = unicode(raw_input('\nNome do aluno: '))
            file = graded % name
            if os.path.exists(file):
                write = raw_input('Aluno existente, sobrescrever? (s/n) ').lower()
                if write in ['s', 'y', 'sim', 'yes']:
                    pass
                else:
                    continue

            idx = unicode(raw_input('\n# da prova: '))
            with open(basepath % idx, 'r') as F:
                obj = simplejson.load(F)
                obj['value'] = 10.0
        except IOError:
            print u'Prova inválida: %s' % (basepath % idx)
            continue

        nota = gp.grade_interactive(obj, print_invalid=2)
        print 'Nota da prova: **%.2f**' % nota

        with open(os.path.join(file), 'w') as F:
            simplejson.dump(obj, F)

elif inpt == 'l':
    basepath = '../bin/m1/l1-%s.json'
    graded = '../bin/m1/graded-lista-%s.json'
    gp = Grader()

    # Cancela algumas questões e dá o ponto de outras de modo que pelo menos 50%
    # da lista esteja garantido: qualquer pontuação conta
    for i in range(5):
        gp.cancel_item(i)
    for i in [5, 6, 7, 8, 11, 12]:
        gp.void_item(i)

    while True:
        try:
            name = unicode(raw_input('\nNome do aluno: '))
            file = graded % name
            if os.path.exists(file):
                write = raw_input('Aluno existente, sobrescrever? (s/n) ').lower()
                if write in ['s', 'y', 'sim', 'yes']:
                    pass
                else:
                    continue

            idx = unicode(raw_input('\n# da lista: '))
            with open(basepath % idx, 'r') as F:
                obj = simplejson.load(F)
                obj['value'] = 4
        except IOError:
            print u'Lista inválida: %s' % (basepath % idx)
            continue

        nota = gp.grade_interactive(obj, print_invalid=2)
        print 'Nota da lista: **%.2f**' % max(0, nota - 2)

        with open(os.path.join(file), 'w') as F:
            simplejson.dump(obj, F)

else:
    print 'Invalid option, quitting...'
