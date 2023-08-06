from tutor.plugins.complexity.number import *

#import collections
#import functools
#import itertools
#import numpy as np
#import operator
#import sympy as sp
#import sys
#
#
#
#
#class Complexity(object):
#    DISPATCH = {
#        sp.Integer: 'int',
#        sp.Rational: 'rat',
#    }
#
#    def __init__(self, sp_decimal=True):
#        self.sp_decimal = sp_decimal
#        self.primes = Primes()
#        if sp_decimal:
#            self.primes.order(11)
#            self.primes._order[10] = 0.5
#
#    def complexity(self, number):
#        number = sp.sympify(number)
#        tt = type(number)
#        for subtype in tt.mro():
#            try:
#                method_name = 'compl_' + self.DISPATCH[subtype]
#            except KeyError:
#                continue
#            else:
#                method = getattr(self, method_name)
#                return method(number)
#        else:
#            raise TypeError('Unsupported type: %s' % tt)
#
#    def compl_int(self, number):
#        '''
#        Complexity of integers
#        '''
#
#        return Integer(number).complexity()
#
#        # Perform special treatment to multiples of 10
##        if self.sp_decimal:
##            pow10 = min(factors.get(2, 0), factors.get(5, 0))
##            if pow10:
##                factors[2] -= pow10
##                if not factors[2]:
##                    del factors[2]
##
##                factors[5] -= pow10
##                if not factors[5]:
##                    del factors[5]
##
##                factors[10] = pow10
#
#    def compl_rat(self, obj):
#        '''
#        Complexity of fractions: simply add the complexity of numerator and 
#        denominator.
#        '''
#
#        numer, denom = obj.as_numer_denom()
#        return self.complexity(numer) + self.complexity(denom)
#
#_complexity = Complexity()
#
#
#def complexity(obj):
#    '''
#    Compute complexity of mathematical object, when defined.
#    
#    For now, only integers are accepted.
#    
#    @param obj: mathematical object
#    '''
#
#    return _complexity.complexity(obj)
#
#if __name__ == '__main__':
#    import doctest
#    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
#    do_tests(Integer)
#
#    for i in range(-5, 101):
#        print '%s) %s' % (i, complexity(i))
#
#    sorted = {}
#    nums = [ (i, complexity(i)) for i in range(1001) ]
#    for i, c in nums:
#        sorted.setdefault(c, []).append(i)
#    sorted = sorted.items()
#    sorted.sort(key=lambda x: x[0])
#    for k, v in sorted:
#        if k < 10:
#            print '%2.1f: %s' % (k, v)
#
#
