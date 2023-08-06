from maple import M

class WrongDiff(object):
    """See examples in http://mathmistakes.info/mistakes/calculus/index.html
    """
    def __init__(self, func, var, n):
        self.func = func
        self.var = var
        self.ntimes = n
        
    def wrong_diff(self):
        pass
    
    def __call__(self, ntries=10):
        if ntries < 0:
            raise ValueError("Could not come up with a bad derivative for "
                             "'%s' with respect to '%s'." % (self.func, self.var))
        res = self.wrong_diff()
        if res == M.diff(self.func, self.var):
            return self(ntries - 1)
        return res

def wrong_diff(func, var, n):
    """
    Return a wrong derivative of function 'func' with respect to 'var'
    """
    
    return WrongDiff(func, var, n)()