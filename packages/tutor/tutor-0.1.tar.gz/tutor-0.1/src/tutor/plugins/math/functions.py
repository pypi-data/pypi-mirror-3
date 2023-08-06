from maple import M

class Function(object):
    def __init__(self, vars, difficulty):
        self.func = M.unapply(func, *vars)
        self.expr = func

class Function1D(Function):
    pass

class func(Function):
    def __init__(self, vars, difficulty=1):
        super(type(self), self).__init__(vars, difficulty=1)
        
class convex(Function):
    def __init__(self, vars, difficulty=1):
        super(type(self), self).__init__(vars, difficulty=1)
    
class concave(Function):
    def __init__(self, vars, difficulty=1):
        super(type(self), self).__init__(vars, difficulty=1)
    
class poly(Function):
    def __init__(self, vars, difficulty=1):
        super(type(self), self).__init__(vars, difficulty=1)
        
class polyrat(Function):
    def __init__(self, vars, difficulty=1):
        super(type(self), self).__init__(vars, difficulty=1)
             
class trig(Function):
    def __init__(self, vars, difficulty=1):
        super(type(self), self).__init__(vars, difficulty=1)

class trigh(Function):
    def __init__(self, vars, difficulty=1):
        super(type(self), self).__init__(vars, difficulty=1)

class special(Function):
    def __init__(self, vars, difficulty=1):
        super(type(self), self).__init__(vars, difficulty=1)

class harmonic(Function):
    def __init__(self, vars, difficulty=1):
        super(type(self), self).__init__(vars, difficulty=1)

class differentiable(Function1D):
    def __init__(self, vars, difficulty=1):
        super(type(self), self).__init__(vars, difficulty=1)

class integrable(Function1D):
    def __init__(self, vars, difficulty=1):
        super(type(self), self).__init__(vars, difficulty=1)

class minimizer2D(object):
    def __init__(self, func, vars=(M.x, M.y)):
        self.func = func
        self.vars = vars
        
    def grad(self):
        """
        Gradient of function.
        """
        
        return [ M.diff(self.func, var) for var in self.vars ]
    
if __name__ == '__main__':
    x, y = M.x, M.y
    f = func(x, difficulty=2)
    