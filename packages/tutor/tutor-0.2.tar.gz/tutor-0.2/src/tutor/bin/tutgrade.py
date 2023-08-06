#!/usr/bin/python
#-*-coding: utf8-*-
import argparse
import tutor.version
from tutor.bin import util
from tutor import grading

def get_parser():
    '''Configure parser'''
    parser = argparse.ArgumentParser(
      description='View Py-Tutor objects.',
      prog='tutgrade', add_help=True, version='%%(prog)s %s' % tutor.version.VERSION)

    parser.add_argument('--exam', '-e', help='exam file')
    parser.add_argument('--classroom', '-c', help='classroom file')
    parser.add_argument('--save_to', '-s', help='save destination')
    parser.add_argument('--debug', '-d', action='store_true', help='print tracebacks')
    return parser

@util.main(get_parser())
def main(exam=None, classroom=None, save_to=None):
    '''tutgrade [-e exam] [-c classroom] [-s save_to]'''

    corr = grading.iExamFileCorrection(exam_f=exam, classroom_f=classroom, save_to=save_to)
    corr.loop()

if __name__ == '__main__':
    main([])
#    main(['question', 'commit', 'foo' , '10'])
