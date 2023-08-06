#!/usr/bin/python
#-*-coding: utf8-*-
import argparse
import tutor.version
from tutor.bin import util
from tutor.util.fs_util import copy_fs

def get_parser():
    '''Configure parser'''
    parser = argparse.ArgumentParser(
      description='Commit changes to objects of the Py-Tutor system.',
      prog='tutcommit', add_help=True, version='%%(prog)s %s' % tutor.version.VERSION)

    parser.add_argument('file', help='file to save new object')
    parser.add_argument('size', help='number of objects to create', type=int)
    parser.add_argument('--final', '-f', action='store_true', help="marks as a final commit")
    parser.add_argument('--debug', '-d', action='store_true', help='print tracebacks')
    return parser

@util.main(get_parser())
def main(file, size, final=False, **kwds): #@ReservedAssignment
    '''tutcommit "fname.ext" "size" [--final]'''

    obj = util.openpath(file)
    name, _ext = util.ext_pair(file)
    if util.file_exists(name + '-src') and hasattr(obj, 'src'):
        copy_fs(name + '-src', obj.src)
    obj.commit(size, final=final)
    util.savepath(obj, file)

if __name__ == '__main__':
    main(['foo.qst', '10'])
#    main(['question', 'commit', 'foo' , '10'])
