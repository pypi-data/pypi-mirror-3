#!/usr/bin/python
#-*-coding: utf8-*-
import argparse
import tutor.version
from tutor.bin import util

def get_parser():
    '''Configure parser'''
    parser = argparse.ArgumentParser(
      description='Adds questions to exam files.',
      prog='tutaddq', add_help=True, version='%%(prog)s %s' % tutor.version.VERSION)

    parser.add_argument('file', help='exam file')
    parser.add_argument('--question', '-q', dest='questions', action='append', help="question to be added to exam")
    parser.add_argument('--commit', '-c', help='commit after adding questions', type=int)
    parser.add_argument('--final', '-f', action='store_true', help="marks as a final commit")
    parser.add_argument('--debug', '-d', action='store_true', help='print tracebacks')
    return parser

@util.main(get_parser())
def main(file, questions=[], **kwds): #@ReservedAssignment
    '''tutaddq "fname.exm" -q "f1.exm" -q "f2.exm"'''

    exm = util.openpath(file)
    exm.add_question(*map(util.openpath, questions))
    if kwds.get('commit', None):
        exm.commit(kwds['commit'], final=kwds.get('final', False))

    util.savepath(exm, file)

if __name__ == '__main__':
    import tutnew, tutview, os
    os.chdir('/tmp')
    tutnew.main('foo.exm -fd --title SomeTitle'.split())
    tutnew.main('foo.qst -fd --commit 10'.split())
    tutnew.main('bar.qst -fd --commit 10'.split())
    main('foo.exm  -q foo.qst -q bar.qst --commit 10'.split())
    tutview.main('foo.exm -d'.split())
