#-*- coding: utf8 -*-
from tutor.visualization import base, exam
from tutor.data.tutor_lib import get_exam
from tutor.transforms import creation
import simplejson, time
import os

def make_exams(exam_name, N, disp=True, dir='dumps', barcode='', each_pdf=False):
    '''
    Make N exams from given template
    '''
    #TODO: make a decent interface

    exam_model = get_exam(exam_name)
    vis_tex = exam.Tex(True)
    vis_tex_inline = exam.Tex(False)
    vis_pdf = base.Pdf(vis_tex)
    all_exams = {}
    tex_items = []
    for i in range(N):
        if disp: print('Creating text %s...' % (i + 1))
        fname = '%s/%s%s.json' % (dir, barcode, i)

        # Get already rendered
        if os.path.exists(fname):
            with open(fname) as F:
                obj = simplejson.load(F)
        else:
            t0 = time.time()
            obj = creation.new_exam(exam_model)
            if disp: print 'Object created in %0.2f sec' % (time.time() - t0)
            if barcode:
                msg = barcode if isinstance(barcode, str) else barcode
                obj['barcode'] = msg + str(i)
            with open(fname, 'w') as F:
                simplejson.dump(obj, F)

        path = '%s/%s%s.tex' % (dir, barcode, i)
        if not os.path.exists(path):
            vis_tex.dump(obj, path)

        if each_pdf:
            path = '%s/%s%s.pdf' % (dir, barcode, i)
            if not os.path.exists(path):
                t0 = time.time()
                vis_pdf.dump(obj, path)
                print 'pdf: %0.2f sec' % (time.time() - t0)

        tex_items.append(vis_tex_inline.render(obj))
        all_exams[i] = obj

    with open('%s/%sall_exams.json' % (dir, barcode), 'w') as F:
        simplejson.dump(all_exams, F)

    with open('%s/all_exams.tex' % dir, 'w') as F:
        data = '\n\\cleardoublepage{}\n'.join(tex_items)
        F.write(base.Tex.head + data + base.Tex.tail)

    if each_pdf:
        cwd = os.getcwd()
        try:
            os.chdir(dir)
            cmd = 'pdftk *.pdf cat output all_exams.pdf'
            os.system(cmd)
        finally:
            os.chdir(cwd)

    return all_exams

if __name__ == '__main__':
    M = 5
    N = 10
    tt = 'substitutiva'
#    tt = 'prova'
#    tt = 'lista'
    dir = 'm%s' % M
    dir = '%s-%s' % (tt, M)
    make_exams('cálculo 3/módulo %s/%s' % (M, tt), N=N, disp=True, dir=dir, barcode='%s%s-' % (tt[0], M))

