#!/usr/bin/python
#-*-coding: utf8-*-
import os
import sys
import argparse
from fs.opener import fsopen
import fs.tempfs
import tutor.version
from tutor.visualization import pdflatex
from tutor.bin import util

def get_parser():
    '''Configure parser'''
    parser = argparse.ArgumentParser(
      description='View Py-Tutor objects.',
      prog='tutview', add_help=True, version='%%(prog)s %s' % tutor.version.VERSION)

    parser.add_argument('file', help='input file')
    parser.add_argument('--mark-correct', dest='mark_correct', action='store_true', help='mark correct answers (for debugging)')
    parser.add_argument('--output', '-o', help='output PDF file')
    parser.add_argument('--program', '-p', help='PDF file viewer')
    parser.add_argument('--debug', '-d', action='store_true', help='print tracebacks')
    return parser

@util.main(get_parser())
def main(file, mark_correct=False, output=None, program='evince'):
    '''tutview "file_name" [-o outfile] [-p pdfviewer] [-d] [--mark-correct]'''

    data = pdflatex(util.openpath(file), mark_correct=mark_correct)
    if output:
        with fsopen(output, 'w') as F:
            F.write(data)
    else:
        base = fs.tempfs.TempFS()
        with base.open('main.pdf', 'w') as F:
            F.write(data)
        path = base.getsyspath('main.pdf')
        os.system('%s %s' % (program, path))

if __name__ == '__main__':
    main(['foo.qst', '-h'])
#    main(['question', 'commit', 'foo' , '10'])
