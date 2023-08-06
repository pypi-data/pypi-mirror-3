#-*- coding: utf8 -*-
from tutor.data.tutor_lib import get_exam
from tutor.transforms import creation
from chips.jsonlib.util import copy
from tutor.config import schemas

class Correction(object):
    def __init__(self, exam, update=True):
        if update:
            self.exam = exam
        else:
            self.exam = copy(exam)

        idx = self._lobj_next_node(self.exam['content'][0], 0)
        self._curr = [0, idx]

    def current(self):
        '''
        Return current node in correction job
        '''
        a, b = self._curr
        return self.exam['content'][a]['content'][b]

    def next(self):
        '''
        Return the current node and update the next one. Raises an StopIteration 
        after the next valid node
        '''

        a, b = self._curr
        if (a is None) or (b is None):
            raise StopIteration

        # Return value
        node = self.current()
        exam = self.exam

        # Check if current question still has pending nodes
        lobj = exam['content'][a]
        b = self._lobj_next_node(lobj, b + 1)
        if b is None:
            try:
                a += 1
                lobj = exam['content'][a]
            except IndexError:
                a = None
            else:
                b = self._lobj_next_node(lobj, 0)
        self._curr = [a, b]

        return node

    def _lobj_next_node(self, lobj, curr):
        try:
            nodes = lobj['content'][curr:]
        except IndexError:
            return None
        else:
            for node in nodes:
                if node['type'] in schemas.QUESTION_NODES:
                    return curr
                else:
                    curr += 1
            else:
                return None

    def compute_grade(self, update=True):
        pass

    def __iter__(self):
        return self

class CorrectionJob(object):
    def __init__(self, template):
        self.template = template
        self._cancelled = set([])
        self._give_grade = set([])

    def cancel_question(self, q_id):
        pass

class iCorrection(Correction):
    def __init__(self, charstream=''):
        pass


tmpl = get_exam('cálculo 3/módulo 4/prova')
obj = creation.new_exam(tmpl)
corr = Correction(obj)
for o in corr:
    print o


def corrigir_prova(st, cod_prova, ntotal=8, manual=[2, 3], values=[1, 1, 1, 1, 1, 1, 2, 0], names='1A 1B 2A 2B 3A 3B 4 5'.split()):
    st = st.lower()
    if len(st) != ntotal:
        raise ValueError('Tamanho incompatível: esperava %s, obteve %s' % (ntotal, len(st)))
    notas = {'-': 0, '+': None, ' ': 0}
    notas = [ notas.get(c, c) for c in st ]
    notas = [ (n if n is not None else values[i]) for i, n in enumerate(notas) ]

    for idx, v in enumerate(values):
        if v == 0:
            notas[idx] = 0

    for idx in manual:
        if isinstance(notas[idx], str):
            raise ValueError('Necessário dizer nota de item %s manualmente' % names[idx])

    it_notas = iter(enumerate(notas))
    exam = modulo[u'cálculo 3/módulo 3/prova::%s' % cod_prova]
    exam = to_value(exam)
    letters = list(string.ascii_lowercase)
    for lobj in exam['content']:
        for item in lobj['content']:
            ivalue, c = it_notas.next()
            if isinstance(c, str):
                idx = letters.index(c)
                value = item['items'][idx].get('value', 0)
                all_values = [ item.get('value', 0) for item in item['items'] ]
                mvalue = max(all_values)
                value *= values[ivalue] / mvalue
                if value != values[ivalue]:
                    midx = all_values.index(mvalue)
                    letter = string.ascii_lowercase[midx]
                    print '  %s) correta: %s, nota: %s' % (names[ivalue].rjust(3), letter, value)
            else:
                value = c
            notas[ivalue] = value

    #print list(zip(notas, values))
    return sum(notas) / float(sum(values)) * 10

def rotina_corr(type='prova', kwds={}, del_items=[]):
    cod_prova = raw_input('Codigo: ')
    try:
        exam = modulo[u'cálculo 3/módulo 3/%s::%s' % (type, cod_prova)]
    except KeyError:
        print 'Erro: prova %s não encontrada!' % cod_prova
    while True:
        try:
            gabarito = raw_input('Gabarito: ')
            for i in del_items:
                gabarito = gabarito[:i] + gabarito[i + 1:]
            print '-' * 40
            print 'Erros:'
            print '-' * 40
            print 'Nota: %0.1f' % corrigir_prova(gabarito, cod_prova, **kwds)
        except ValueError as ex:
            print 'Erro: %s' % ex
            print 'Digite o gabarito novamente'
        else:
            break
