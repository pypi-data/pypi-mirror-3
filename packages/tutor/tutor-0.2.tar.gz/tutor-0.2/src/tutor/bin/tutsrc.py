#!/usr/bin/python
#-*-coding: utf8-*-
import argparse
import tutor.version
from tutor.bin import util
from tutor.util.fs_util import copy_fs

def get_parser():
    '''Configure parser'''
    parser = argparse.ArgumentParser(
      description='Extract source of Py-Tutor questions.',
      prog='tutsrc', add_help=True, version='%%(prog)s %s' % tutor.version.VERSION)

    parser.add_argument('file', help='file to save new object')
    parser.add_argument('--force', '-f', action='store_true', help="overwrites pre-existing object")
    parser.add_argument('--debug', '-d', action='store_true', help='print tracebacks')
    return parser

@util.main(get_parser())
def main(file, force=False, **kwds): #@ReservedAssignment
    '''tutsrc "fname.ext" [--force]'''

    fname = file
    src = util.openpath(fname)
    name, ext = util.ext_pair(fname)
    util.assure_no_file(name + '-src', not force)
    try:
        src = src.src
    except AttributeError:
        raise ValueError('unsupported file type: %s' % ext)
    copy_fs(src, name + '-src')

if __name__ == '__main__':
    main(['foo.qst', ])
#    main(['question', 'commit', 'foo' , '10'])
