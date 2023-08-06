#!/usr/bin/python
#-*-coding: utf8-*-
import sys
import argparse
import tutor.version
from tutor.bin import util
from tutor import types

def get_parser():
    '''Configure parser'''
    parser = argparse.ArgumentParser(
      description='Create Py-Tutor objects.',
      prog='tutnew', add_help=True, version='%%(prog)s %s' % tutor.version.VERSION)

    parser.add_argument('file', help='file to save new object')
    parser.add_argument('--force', '-f', action='store_true', help="overwrites pre-existing object")
    parser.add_argument('--main', '-m', help="path to main source file of a question")
    parser.add_argument('--namespace', '-n', help="path to namespace file of a question")
    parser.add_argument('--author', '-a', help="set author's name")
    parser.add_argument('--title', '-t', help="set an exam's title")
    parser.add_argument('--commit', '-c', help="executes a commit after creating object", type=int)
    parser.add_argument('--course_name', '-cn', help="set a classroom course name")
    parser.add_argument('--debug', '-d', action='store_true', help='print tracebacks')
    return parser

@util.main(get_parser())
def main(file, force=False, **kwds): #@ReservedAssignment
    '''tutnew "fname.ext" [-a author] [-t title] [-d]'''

    fname = file
    name, ext = util.ext_pair(fname)
    util.assure_no_file(fname, not force)
    commit = kwds.pop('commit', None)

    if ext == '.qst':
        if 'main' in kwds:
            main = kwds.pop('main')
            kwds['main_t'] = util.ext_pair(main)[1][1:]
            with open(main) as F:
                kwds['main_data'] = F.read().decode('utf8')

        if 'namespace' in kwds:
            namespace = kwds.pop('namespace')
            kwds['namespace_t'] = util.ext_pair(namespace)[1][1:]
            with open(namespace) as F:
                kwds['namespace_data'] = F.read().decode('utf8')

        new = types.QuestionPool(name, **kwds)
    elif ext == '.exm':
        new = types.ExamPool(name, **kwds)
    elif ext == '.cls':
        course_name = kwds.pop('course_name', name.replace('_', ' ').title())
        new = types.Classroom(course_name, **kwds)
    else:
        raise ValueError('could not create file: unknown extension: %s' % ext)

    if commit is not None:
        new.commit(commit)

    util.savepath(new, fname)

if __name__ == '__main__':
    #main(['foo.exm', '-fd'])
    main(['foo.cls', '-fd'])
