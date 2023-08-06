#===============================================================================
#                         USAR TRANSFORMATION/GRADING
#===============================================================================

from tutor.visualization import base, exam, learning_obj

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
if False:
    while True:
        print
        print '=' * 40
        print 'PROVA'
        print
        rotina_corr()
    #    print
    #    print '-' * 40
    #    print 'LISTA'
    #    print
    #    kwds = dict(
    #        ntotal=14,
    #        manual=[],
    #        values=[2, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    #        names='1 2 3A 3B 4 5a 5b 7a 7b 8a 8b 9a 9b 10'.split())
    #    rotina_corr(type='lista', kwds=kwds, del_items=[7])

