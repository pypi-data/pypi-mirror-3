 #-*- coding: utf8 -*-
from grading import Grader
import os
import simplejson

basepath = '../bin/m3/p3-%s.json'
graded = '../bin/m3/graded-%s.json'
gp = Grader()

lbasepath = '../bin/m3/l3-%s.json'
lgraded = '../bin/m3/graded-lista-%s.json'
lgp = Grader()
lgp.void_item(5)

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

    try:
        lfile = lgraded % name
        if os.path.exists(lfile):
            write = raw_input('Aluno existente, sobrescrever? (s/n) ').lower()
            if write in ['s', 'y', 'sim', 'yes']:
                pass
            else:
                continue

        lidx = unicode(raw_input('\n# da lista: '))
        with open(lbasepath % lidx, 'r') as F:
            lobj = simplejson.load(F)
            lobj['value'] = 4
    except IOError:
        print u'Lista inválida: %s' % (lbasepath % idx)
        continue

    nota = lgp.grade_interactive(lobj, print_invalid=2)
    print 'Nota da lista: **%.2f**' % max(0, nota - 2)

    with open(os.path.join(lfile), 'w') as F:
        simplejson.dump(lobj, F)
