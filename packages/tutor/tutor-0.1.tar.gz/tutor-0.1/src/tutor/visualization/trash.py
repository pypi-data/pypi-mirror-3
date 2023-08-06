from tutor.visualization import base, exam, learning_obj

if __name__ == '__main__2':
    def test_lobj():
        from tutor.data.tutor_lib import get_learning_obj
        obj = get_learning_obj('examples/lyx_simple')
        vis = learning_obj.Tex(True)
        vis.dump(obj)

    from tutor.data.tutor_lib import get_exam, get_learning_obj
    from tutor.transforms import creation
#    obj = get_learning_obj('examples/lyx_simple')
#    vis = TexLearningObj(True)
#    vis.dump(obj, '~/foo.tex')
#    vis = Pdf(vis)
#    vis.dump(obj, '~/foo.pdf')


#    exam = get_exam('cálculo 3/módulo 4/prova')
#    exam = creation.Exam(exam).new()
#    exam['barcode'] = 'foo'
#    vis = TexExam(True)
#    vis.dump(exam, '~/foo.tex')
#    vis = Pdf(vis)
#    vis.dump(exam, '~/foo.pdf')

    vistex = exam.Tex(True)
    vis = exam.Response()
#    vis.dump(exam)

    def to_value(obj):
        try:
            obj[u'value'] = obj['grade']
            del obj['grade']
        except KeyError:
            pass
        items = obj.get('content', obj.get('items', []))
        for item in items:
            to_value(item)
        return obj

    import pprint
#    pprint.pprint(exam)

    import simplejson
    with open('lista4-dumps/all_exams.json') as F:
        lista = simplejson.load(F).values()[3]
    exam.Response().dump(lista)


    with open('../_old/db/json_consolidated') as F:
        conflicts, unique = simplejson.load(F).items()
    modulo = unique[1]
    mod_extra = conflicts[1]

    # Inicia correção
#    print '\n'.join(modulo.keys())
#    cod_prova = '60'
#    cod_prova = '43'
#    prova = modulo[u'cálculo 3/módulo 3/prova::%s' % cod_prova]
#    prova = to_value(prova)
#    vis.dump(prova)

#    cod_lista = '183'
#    prova = modulo[u'cálculo 3/módulo 3/lista::%s' % cod_lista]
#    prova = to_value(prova)
#    vis.dump(prova)
#    vistex.dump(prova)

