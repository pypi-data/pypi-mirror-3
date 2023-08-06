from __future__ import print_function
from future_builtins import *
import random

class Mapping(object):
    def __init__(self, N, seed=None):
        self.N = N
        self.seed = seed
        lst = list(range(N))
        
        if seed is None:
            self.mapping = list(zip(lst, lst))
        else:
            try:
                M = 1 # probably it is good to mess with this parameter
                random.seed(seed + M)
                random.shuffle(lst)
                self.mapping = list(zip(range(N), lst))
            finally:
                random.seed() # reset seed
        
    def apply(self, list):
        new_list = [ None ] * len(list)
        for i, j in self.mapping:
            new_list[i] = list[j]
        return new_list
    
    def unapply(self, list):
        mapping = self.mapping
        try:
            self.mapping = ( (j,i) for (i,j) in self.mapping )
            return self.apply(list)
        finally:
            self.mapping = mapping
            
    def __str__(self):
        return "<Maping object '%s'>" % self.mapping
       
if __name__ == '__main__':
    pass
 