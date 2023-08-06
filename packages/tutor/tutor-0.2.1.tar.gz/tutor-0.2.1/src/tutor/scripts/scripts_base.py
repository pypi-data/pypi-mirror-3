#-*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from future_builtins import * #@UnusedWildImport

class ScriptError(AssertionError):
    pass

#------------------------------------------------------------------------------
#                       USEFUL FUNCTIONS IN PYTHON LIB
#------------------------------------------------------------------------------
from datetime import datetime #@UnusedImport
import contextlib
import inspect

@contextlib.contextmanager
def display_block(name='anonymous'):
    # __enter__
    old_globals = dict(inspect.currentframe(2).f_globals)
    old_globals = dict((k, id(v)) for (k, v) in old_globals.items())

    # execute block
    yield

    # __exit__
    new_globals = dict(inspect.currentframe(2).f_globals)
    diff = {}
    for (k, v) in new_globals.items():
        v_id = id(v)
        if old_globals.get(k, 1) != v_id:
            diff[k] = v

    print('\n' + name)
    print('-' * len(name))
    diff_items = diff.items()
    diff_items.sort(key=lambda item: item[0])
    for item in diff_items:
        if not item[0].startswith('_'):
            print('    %s = %s' % item)

display_vars = display_block

#------------------------------------------------------------------------------
#                             USEFUL RANDOMIZERS
#------------------------------------------------------------------------------
import random as mrandom
_random = mrandom
from random import randint, uniform, random, sample, shuffle, choice #@UnusedImport

def oneof(*args):
    """Return a random value from its arguments. 
    
    Can be called in two different ways:
        oneof(sequence) --> returns an element of the sequence
        oneof(arg1, arg2, ...) --> returns one of the arguments
        
    Examples
    --------
    
    >>> x = oneof(1, 2, 3)
    >>> x in [1, 2, 3] # x can be 1, 2 or 3
    True
    
    >>> nums = range(10)
    >>> x = oneof(nums)
    >>> 0 <= x < 10 # x can be 0, 1, ..., or 10
    True
    """

    if not args:
        raise TypeError('cannot be called with empty arguments!')
    elif len(args) == 1:
        try:
            return _random.choice(list(args[0]))
        except TypeError:
            raise TypeError("first argument must be a sequence or more than one argument must be given, got '%s'" % args)
    else:
        return _random.choice(args)

def shuffled(lst, inplace=False):
    '''
    Return a shuffled copy of a list or sequence.
    
    If 'inplace' is True, the argument is modified and the return value is the 
    list itself.
    '''

    if not inplace:
        lst = list(lst)
    _random.shuffle(lst)
    return lst

class Answers(list):
    last = None

    def __init__(self):
        super(Answers, self).__init__()
        Answers.last = self
        self.has_distractor = False

    def append(self, obj):
        if self.has_distractor:
            raise ValueError('cannot append answer after yielding a distractor')
        if obj in self:
            raise ScriptError
        else:
            super(Answers, self).append(obj)

    def append_distractor(self):
        self.has_distractor = True
        if not self:
            super(Answers, self).append(0)

        while True:
            if 0.5 > _random.random():
                ans1, ans2 = oneof(self), oneof(self)
                new = (ans1 + ans2) / 2
            elif 0.5 > _random.random():
                ans1, ans2 = oneof(self), oneof(self)
                new = (ans1 + ans2) / 2 + oneof(1, 2)
            else:
                new = oneof(self) + oneof(1, -1, 2, -2, 3, -3)
            if new not in self:
                super(Answers, self).append(new)
                break

def answer(obj, clear=False):
    '''Marks object as a unique answer.'''

    if clear:
        Answers.last = None

    if Answers.last is None:
        ans = Answers()
    else:
        ans = Answers.last
    ans.append(obj)
    return obj

def distractor():
    '''Creates a distractor from the current set of answers.'''

    Answers.last.append_distractor()
    return Answers.last[-1]
