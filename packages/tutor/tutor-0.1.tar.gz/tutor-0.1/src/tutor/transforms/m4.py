 #-*- coding: utf8 -*-
from grading import Grader
import os
import simplejson

basepath = '../bin/m4/p4-%s.json'
graded = '../bin/m4/graded-%s.json'
gp = Grader()

lbasepath = '../bin/m4/l4-%s.json'
lgraded = '../bin/m4/graded-lista-%s.json'
lgp = Grader()
lgp.void_item(2)

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
            items = lobj['content'][-1]['content'][1]['items']
            for it in items:
                if it['id'] == 0:
                    it['value'] = 1.0
    except IOError:
        print u'Lista inválida: %s' % (lbasepath % lidx)
        continue

    nota = lgp.grade_interactive(lobj, print_invalid=2)
    print 'Nota da lista: **%.2f**' % max(0, nota - 2)

    with open(os.path.join(lfile), 'w') as F:
        simplejson.dump(lobj, F)
