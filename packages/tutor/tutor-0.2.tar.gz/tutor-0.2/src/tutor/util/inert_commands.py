'''
Inert versions of commands in tutor.scripts that do not print any messages to
the stdout. This optimizes things a little bit. 
'''
import contextlib

@contextlib.contextmanager
def display_block(st):
    '''Do nothing version of tutor.scripts.display_block'''

    yield

from tutor.scripts import Answers
Answers.last = None
