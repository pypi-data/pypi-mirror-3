#!/usr/bin/python
#-*-coding: utf8-*-
import argparse
import pyson
import tutor.version
from tutor.bin import util
from tutor import permanence

def get_parser():
    '''Configure parser'''
    parser = argparse.ArgumentParser(
      description='Commit changes to objects of the Py-Tutor system.',
      prog='tutcommit', add_help=True, version='%%(prog)s %s' % tutor.version.VERSION)

    parser.add_argument('file', help='file to save new object')
    parser.add_argument('--debug', '-d', action='store_true', help='print tracebacks')
    return parser

@util.main(get_parser())
def main(file, ** kwds): #@ReservedAssignment
    '''tutcommit "fname.ext" "size" [--final]'''

    pyson.sprint(permanence.openpathjson(file))

if __name__ == '__main__':
    main(['foo.qst', '10'])
#    main(['question', 'commit', 'foo' , '10'])
