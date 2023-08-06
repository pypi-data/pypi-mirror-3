from plasTeX import Command, Environment, Base
import plasTeX

def ProcessOptions(*args, **kwds):
    print 'loading quiztutor_latex module'
    
#
# Metadata commands
#
class _opt(Command):
    pass

class _cmd(Command): 
        args = ''
        forcePars = True
        
        def digest(self, tokens):
            for tok in tokens:
                if tok.isElementContentWhitespace:
                    continue
                tokens.push(tok)
                break
            self.digestUntil(tokens, _cmd)
            if self.forcePars:
                self.paragraphs()
    
class metadata(_opt):
    args = 'content'
    class author(_cmd): pass
    class creationdate(_cmd): pass
    class difficulty(_cmd): pass
    class quiztype(_cmd): pass
    class status(_cmd): pass
    
class options(_opt):
    args = 'content'
    class printlogo(_cmd): pass
    class printheading(_cmd): pass
    class printbarcode(_cmd): pass
    class querystudentinfo(_cmd): pass
    class numbits(_cmd): pass
  
class questions(_opt):
    args = 'content'
    class basedir(_cmd): 
        args = 'path'
