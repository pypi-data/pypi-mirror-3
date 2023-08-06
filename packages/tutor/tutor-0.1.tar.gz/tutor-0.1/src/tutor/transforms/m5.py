 #-*- coding: utf8 -*-
from grading import Grader
import os
import simplejson

basepath = '../bin/m5/p5-%s.json'
graded = '../bin/m5/graded-%s.json'
gp = Grader()

while True:
    try:
        do_write = True
        name = unicode(raw_input('\nMatrícula: '))
        file = graded % name
        if os.path.exists(file):
            write = raw_input('Aluno existente, sobrescrever? (s/n) ').lower()
            do_write = write in ['s', 'y', 'sim', 'yes']

        if do_write:
            idx = unicode(raw_input('\n# da prova: '))
            with open(basepath % idx, 'r') as F:
                obj = simplejson.load(F)
                obj['value'] = 10.0
            nota = gp.grade_interactive(obj, print_invalid=2)
            print 'Nota da prova: **%.2f**' % nota

            with open(os.path.join(file), 'w') as F:
                simplejson.dump(obj, F)

    except IOError:
        print u'Prova inválida: %s' % (basepath % idx)
        continue
