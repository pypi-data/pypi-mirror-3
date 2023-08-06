from plasTeX import Command, Base

def ProcessOptions(*args, **kwds):
    pass
    #print 'loading tutor_latex module'

#===============================================================================
# Environments
#===============================================================================
class _env(Base.List):
    forcePars = True
    class item(Base.List.item):
        forcePars = True

class items(Base.List):
    pass

class truefalse(_env):
    args = '[options:str]'

class multiplechoice(_env):
    args = '[options:str]'

class association(_env):
    args = '[options:str]'

class introtext(_env):
    args = '[options:str]'

#===============================================================================
# Commands 
#===============================================================================
class feedback(Command):
    args = 'text'

class comment(Command):
    args = 'text'

class solution(Command):
    args = 'text'

class answer(Command):
    args = 'text'

class grade(Command):
    args = 'text'

class associatewith(Command):
    args = 'text'
