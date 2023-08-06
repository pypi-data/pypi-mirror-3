from cStringIO import StringIO
import fs.errors
import fs.osfs
from fs.opener import fsopen
import pyson
from tutor.util.file_operations import copy_fs
from tutor.util import pdfcreate
from tutor.visualization import render
from tutor.permanence import dumps, load
from tutor import types

def f_exists(fpath, fname=None):
    fname = fpath if fname is None else fname
    base, name = fs.path.split(fpath)
    base = fs.osfs.OSFS(base)
    return base.exists(name)

def check_no_f(fpath, fname=None, check=True):
    if check:
        fname = fpath if fname is None else fname
        if f_exists(fpath):
            raise fs.errors.ResourceError('file already exists: %s' % fname)

class Question(object):
    @staticmethod
    def _load_from_name(name):
        assert isinstance(name, unicode)
        with fsopen(name) as F:
            return load(F)

    @staticmethod
    def _save_question(qst, fname):
        base, fname = fs.path.split(fname)
        base = fs.osfs.OSFS(base)
        data = dumps(qst)
        with base.open(fname, 'w') as F:
            F.write(data)

    def new(self, name, force=False, main=None, namespace=None, lyx=False,
            title='<untitled>', author=u'', **opts):
        '''$ tutor question new "name" [--force] [--main foo.lyx] [--namespace bar.py] [--lyx]'''

        # Collects data for main.* and namespace.* files
        data = {}
        for ftype, fname in zip(['main', 'namespace'], [main, namespace]):
            if fname:
                with fsopen(fname) as F:
                    data[ftype] = F.read()

        # Adjusts the lyx parameter if a main.lyx file was given
        if main and main.endswith('.lyx'):
            lyx = True

        # Creates a new question
        fname = name if name.endswith('.qst') else name + '.qst'
        name = fs.path.split(fname)[-1][:-4]
        main_type = 'lyx' if lyx else 'tex'
        author = (author.decode('utf8') if author else '')
        title = (title.decode('utf8') if title else '')
        qst = types.QuestionPool(name, main_t=main_type, author=author, title=title)
        qst.commit(1)

        # Saves main and namespace data, if it exists
        if data:
            src = qst.src
            if namespace:
                with src.open('namespace.py', 'w') as F:
                    F.write(data['namespace'])
            if main:
                with src.open('main.' + main_type, 'w') as F:
                    F.write(data['main'])

        # Save question to file
        check_no_f(name, check=not force)
        self._save_question(qst, fname)

    def commit(self, name, size, **opts):
        '''$ tutor question commit "name" "size"'''

        # Open question
        name = (name if name.endswith('.qst') else name + '.qst').decode('utf8')
        qst = self._load_from_name(name)

        # Check if there is an opened src folder: question_name-src/
        src_folder = name[:-4] + '-src'
        if f_exists(src_folder):
            src = fs.osfs.OSFS(src_folder)
            copy_fs(src, qst.src)

        # Commit changes and dump
        qst.commit(size)
        self._save_question(qst, name)

    def view(self, name, outfile, **opts):
        '''$ tutor question view "name" "outfile"'''

        name = (name if name.endswith('.qst') else name + '.qst').decode('utf8')
        qst = self._load_from_name(name)

        if outfile.endswith('tex'):
            data = render(qst, 'latex').encode('utf8')
        elif outfile.endswith('json'):
            data = pyson.dumps(pyson.json_encode(qst))
        else:
            data = render(qst, 'pdflatex')

        if not outfile.startswith('!'):
            with open(outfile, 'w') as F:
                F.write(data)
        else:
            pdfcreate.view_pdf(StringIO(data))

    def src(self, name, force=False, **opts):
        '''$ tutor question src "name" [--force]'''

        name = (name if name.endswith('.qst') else name + '.qst').decode('utf8')
        qst = self._load_from_name(name)
        src_folder = name[:-4] + '-src'
        check_no_f(src_folder, check=not force)
        src_folder = fs.osfs.OSFS(src_folder, create=True)
        copy_fs(qst.src, src_folder)

class Exam(object):
    @staticmethod
    def _load_from_name(name):
        assert isinstance(name, unicode)
        with fsopen(name) as F:
            return load(F)

    @staticmethod
    def _save_exam(exam, fname):
        base, fname = fs.path.split(fname)
        base = fs.osfs.OSFS(base)
        data = dumps(exam)
        with base.open(fname, 'w') as F:
            F.write(data)

    def new(self, name, force=False, title=None, author=None, **opts):
        '''$ tutor exam new "name" [--force] [--author "A person"] [--title "A title"]'''

        title = ('<untitled>' if title is None else title).decode('utf8')
        author = ('<no author>' if author is None else author).decode('utf8')

        # Creates a new exam
        fname = name if name.endswith('.exm') else name + '.exm'
        name = fs.path.split(fname)[-1][:-4]
        exm = types.ExamPool(name, author=author, title=title)

        # Save question to file
        check_no_f(name, check=not force)
        self._save_exam(exm, fname)

    def addq(self, name, question, force=False, **opts):
        '''$ tutor exam addq "name" "question"'''

        # Open exam
        ename = (name if name.endswith('.exm') else name + '.exm').decode('utf8')
        exam = self._load_from_name(ename)

        # Open question
        qname = (question if question.endswith('.qst') else question + '.qst').decode('utf8')
        qst = Question._load_from_name(qname)
        exam.add_question(qst, overwrite=True)

        # Save exam to file
        self._save_exam(exam, ename)

    def commit(self, name, size, force=False, **opts):
        '''$ tutor exam commit "name" "size"'''

        # Open exam
        name = (name if name.endswith('.exm') else name + '.exm').decode('utf8')
        exam = self._load_from_name(name)

        # Commit
        exam.commit(size)

        # Save exam to file
        self._save_exam(exam, name)

    def view(self, name, outfile, **opts):
        '''$ tutor exam view "name" "outfile"'''

        # Open exam
        name = (name if name.endswith('.exm') else name + '.exm').decode('utf8')
        exam = self._load_from_name(name)

        if outfile.endswith('tex'):
            data = render(exam, 'latex').encode('utf8')
        elif outfile.endswith('json'):
            data = pyson.dumps(pyson.json_encode(exam))
        else:
            data = render(exam, 'pdflatex')

        if not outfile.startswith('!'):
            with open(outfile, 'w') as F:
                F.write(data)
        else:
            pdfcreate.view_pdf(StringIO(data))

    def setvalue(self, name, attr, value, force=False, **opts):
        '''$ tutor exam set "name" "attr" "value"'''

        # Open exam
        name = (name if name.endswith('.exm') else name + '.exm').decode('utf8')
        exam = self._load_from_name(name)

        # Save attribute
        schema = exam.schema[attr]
        setattr(exam, attr, schema.adapt(value.decode('utf8')))

        # Save exam to file
        self._save_exam(exam, name)

class Student(object):
    def new(self, name, **opts):
        print 'creates a new student "%s"' % name

    def delete(self, name, **opts):
        print 'delete student "%s"' % name

    def edit(self, name, **opts):
        print 'edit student "%s"' % name
