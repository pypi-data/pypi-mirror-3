#-*- coding: utf8 -*-
'''
Tutor objects are organized in courses. A Tutor course coordinates a library
of questions and exam files. A course must also be associated with one 
or more classrooms. A classroom consists not only of students and teachers, but 
also tasks such as exams, questionnaires, homework, etc.

To the user, a course is presented as a directory structure with some special
files and sub-folders.
'''
from __future__ import absolute_import, unicode_literals
if __name__ == '__main__':
    __package__ = b'tutor' #@ReservedAssignment
    import tutor #@UnusedImport

import os
import fs.path
import functools
import operator as op
from propertylib import oncedescriptor
from . import permanence
from .util import fs_util
from .util.grab_output import grab_output

def clear_after(**clear):
    def decorator(func):
        @functools.wraps(func)
        def decorated(self, *args, **kwds):
            result = func(self, *args, **kwds)
            self.clear(**clear)
            return result
        return decorated
    return decorator

class Course(object):
    def __init__(self, folder=None):
        if isinstance(folder, basestring):
            from fs.osfs import OSFS
            folder = OSFS(folder, create=True)
        elif folder is None:
            from fs.tempfs import TempFS
            folder = TempFS()

        self.folder = folder
        self.makefolders()

    def makefolders(self):
        '''Creates the initial folders and associate them with FS objects inside
        self.'''

        self.folder.makedir('tmp', allow_recreate=True)
        self.folder.makedir('email', allow_recreate=True)
        self.folder.makedir('questions', allow_recreate=True)
        self.folder.makedir('exams', allow_recreate=True)
        self.folder.makedir('backup', allow_recreate=True)

        files = [ f for f in self.folder.listdir(files_only=True) if f.endswith('.course') ]
        if len(files) == 0:
            fname = 'main.course'
        elif len(files) == 1:
            fname = files[0]
        else:
            fnames = ', '.join(files)
            raise ValueError('more than once course found: %s' % fnames)
        self.course_fname = fname
        self.folder.setcontents(fname, self.default_main())

    def init(self, data=None):
        if data is None:
            data = self.default_main()

    def default_main(self):
        return 'main course!'

    def printfiles(self):
        '''Prints the content of folder'''

        for folder, files in self.folder.walk():
            folder = (folder + '/' if not folder.endswith('/') else folder)
            print(folder)
            for f in files:
                print(fs.path.join(folder, f))

    def open(self, *args, **kwds): #@ReservedAssignment
        '''Opens a file inside folder'''

        return self.folder.open(*args, **kwds)

    #===========================================================================
    # Data queries
    #===========================================================================
    def get_object(self, id, type): #@ReservedAssignment
        '''Queries for a particular object of given `id` and `type`.

        If object is not found, it raises a KeyError.
        '''
        try:
            getter = getattr(self, 'get_%s' % type)
        except AttributeError:
            raise ValueError('invalid type: %s' % type)
        else:
            return getter(id)

    def get_question_pool(self, id): #@ReservedAssignment
        path = self.question_ids[id]
        return self.openpath(path)

    def get_question(self, id, rev, key): #@ReservedAssignment
        return self.get_question_pool(id)[rev, key]

    def get_exam_pool(self, id): #@ReservedAssignment
        path = self.exam_ids[id]
        return self.openpath(path)

    def get_exam(self, id, rev, key): #@ReservedAssignment
        return self.get_exam_pool(id)[rev, key]

    def get_classroom(self, id=None, path=None): #@ReservedAssignment
        path = self.classroom_ids[id]
        return self.openpath(path)

    def get_student(self, id): #@ReservedAssignment
        for path in self.classroom_ids.values():
            try:
                return self.openpath(path).get_student(id)
            except ValueError:
                continue
        else:
            raise ValueError('student not found: %s' % id)

    def get_person(self, id): #@ReservedAssignment
        for path in self.classroom_ids.values():
            try:
                return self.openpath(path).get_student(id)
            except ValueError:
                try:
                    return self.openpath(path).get_teacher(id)
                except ValueError:
                    continue
        else:
            raise ValueError('person not found: %s' % id)

    #===========================================================================
    # Fetching objects 
    #===========================================================================
    def openpath(self, path, conv=False):
        data = self.folder.getcontents(path)
        try:
            return permanence.loads(data, conv)
        except Exception as ex:
            if conv:
                raise
            else:
                print 'Warning: error caught opening %s: %s' % (path, ex)
                return None

    def savepath(self, obj, path):
        data = permanence.dumps(obj)
        self.folder.setcontents(path, data)

    def updatepath(self, path):
        if self.openpath(path, False) is None:
            obj = self.openpath(path, True)
            self.folder.move(path, path + '~')
            self.savepath(obj, path)

    def updateall(self, *args):
        if not args:
            args = ['qst', 'exm', 'cls', 'resps']

        for f in self.filepaths:
            for arg in args:
                if f.endswith('.' + arg):
                    self.updatepath(f)

    def updatebad(self, *args):
        if args is None:
            args = ['qst', 'exm', 'cls', 'resps']

        for f in self.filepaths:
            if f.endswith('#'):
                for arg in args:
                    if f.endswith('.%s#' % arg):
                        self.updatepath(f)
    #===========================================================================
    # Messages
    #===========================================================================
    # messaging between modules

    #===========================================================================
    # Tasks
    #===========================================================================
    # create and execute tasks within the system

    #===========================================================================
    # Properties/descriptors and default values
    #===========================================================================
    closed = False

    @oncedescriptor
    def filepaths(self):
        return set(self.folder.walkfiles())

    @oncedescriptor
    def filenames(self):
        names = {}
        for (folder, fname) in map(os.path.split, self.filepaths):
            paths = names.setdefault(fname, [])
            paths.append(folder)
        return names

    def _getids(self, ext):
        ids = {}
        for fname in (f for f in self.filepaths if f.endswith(ext)):
            ids[getattr(self.openpath(fname), 'id', None)] = fname
        ids.pop(None, None)
        return ids

    @oncedescriptor
    def question_ids(self):
        return self._getids('.qst')

    @oncedescriptor
    def exam_ids(self):
        return self._getids('.exm')

    @oncedescriptor
    def classroom_ids(self):
        return self._getids('.cls')

    def clear(self, **kwds):
        good_kwds = { k for (k, v) in vars(type(self)).items() if isinstance(v, oncedescriptor) }
        if not kwds:
            clear = good_kwds
        else:
            if not good_kwds.issuperset(kwds):
                diff = set(kwds) - good_kwds
                raise TypeError('invalid argument: %s' % diff.pop())
            clear = { k for (k, v) in kwds.items() if v }

        for k in clear:
            self.__dict__.pop(k, None)

    #===========================================================================
    # Clean-up methods
    #===========================================================================
    def clean(self):
        self.clean_correction()

    def clean_correction(self):
        pass

    def close_src(self):
        '''Remove all < question > -src folders from the course's questions'''

        for path in self.folder.walkdirs():
            if path.endswith('-src') and self.folder.exists(path[:-4] + '.qst'):
                self.folder.removedir(path, force=True)
        self.clear(filepaths=True, filenames=True)

    @clear_after(filepaths=True, filenames=True)
    def open_src(self):
        '''Remove all <question>-src folders from the course's questions'''

        for path in self.filepaths:
            if path.endswith('.qst'):
                if self.folder.exists(path[:-4] + '-src'):
                    continue
                question = self.openpath(path)
                if question is None:
                    self.folder.move(path, path + '#')
                else:
                    dest = self.folder.makeopendir(path[:-4] + '-src')
                    fs_util.copy_fs(question.src, dest)

    @clear_after(filepaths=True, filenames=True)
    def re_enable(self):
        for path in self.filepaths:
            if path.endswith('#'):
                self.folder.move(path, path[:-1])

    @clear_after(filepaths=True, filenames=True)
    def conv_files(self):
        for path in self.filepaths:
            if path.endswith('#'):
                obj = self.openpath(path, True)
                self.folder.move(path, path[:-1] + '~')
                self.savepath(obj, path[:-1])

    def aggregate_responses(self):
        '''Aggregate all responses in the corresponding classroom objects.'''

        classrooms = { k: (v, self.openpath(v)) for (k, v) in self.classroom_ids.items() }
        students = []
        for (_p, c) in classrooms.values():
            students.extend(c.students)
        students = { s.id: s for s in students }

        for path in self.filepaths:
            if path.endswith('.resps'):
                resps = self.openpath(path, True)
                print resps, len(resps.responses)
                for resp in resps.responses:
                    student = students[resp.student_id]
                    student.parent.responses.append(resp)
                self.folder.move(path, 'backup/' + path[1:].replace('/', '-') + '~')

        for (path, cls) in classrooms.values():
            self.savepath(cls, path)

    #===========================================================================
    # Other methods
    #===========================================================================
    def close(self):
        if self.closed:
            raise ValueError('Course already closed')

    def __del__(self):
        if not self.closed:
            self.close()

def coursefind(folder=None):
    '''Find a .course file starting from folder (or the current directory)
    climbing up the tree'''

    folder = folder or os.getcwd()
    base = True
    while base:
        files = [ f for f in os.listdir(folder) if f.endswith('.course') ]
        if len(files) == 1:
            return Course(folder=folder)
        if len(files) > 1:
            fnames = (os.path.join(folder, f) for f in files)
            fnames = ', '.join(fnames)
            raise ValueError('more than once course found: %s' % fnames)
        folder, base = os.path.split(folder)
    raise ValueError('course file not found')

COURSE = None
def globalcourse(folder=None):
    '''Return the main course environment.'''

    global COURSE
    if COURSE is None:
        COURSE = coursefind(folder)
        return COURSE
    else:
        return COURSE

#from .permanence import loadjson
#c = course = coursefind('../../course_example')
#clsa, clsb = c.openpath('turma_aa.cls'), c.openpath('turma_bb.cls')

def makecsv(cls):
    scores = {}
    exam_date = {}
    for r in cls.responses:
        exam_ref = tuple(r.objref[:2])
        if exam_ref in exam_date:
            if r.ctime < exam_date[exam_ref]:
                exam_date[exam_ref] = r.ctime
        else:
            exam_date[exam_ref] = r.ctime

        score = scores.setdefault(r.student_id, {})
        score[exam_ref] = r.score

    exams = sorted(exam_date.items(), key=op.itemgetter(1))
    exams = [ k for (k, _) in exams ]

    students = { s.id: s for s in cls.students }

    with grab_output(encoding='utf8') as data:
        print 'Matrícula; Nome; %s' % ('; '.join('P%s' % (i + 1) for i in range(len(exams))))
        for sid in sorted(students):
            line = [sid, students[sid].full_name]
            for exam in exams:
                try:
                    line.append(str(scores[sid].get(exam, '')))
                except KeyError:
                    line.append('')
            print '; '.join(line)

    return data

if __name__ == '__main__':
    os.chdir('../../course_example')
    course = globalcourse()
    course.aggregate_responses()
    print len(course.openpath('turma_aa.cls').responses)
    print len(course.openpath('turma_bb.cls').responses)
    print('OK!')
