from plasTeX import Command, Environment, Base
import plasTeX

def ProcessOptions(*args, **kwds):
    pass
    #print 'loading tutor_latex module'
    
class python(Base.verbatim):
    args = '[options] code'
    def digestfalse(self, tokens):
        Environment.digest(self, tokens)
        code = []
        for t in tokens:
            code.append(t.source)
            if type(t) is python:
                break
        print ''.join(code)
                
class pyr(Base.verb):
    args = '[ converter ] content'
       

#
# Metadata commands
#
class metadata(Command):
    args = 'content'

    class _metacmd(Command): 
        args = ''
        forcePars = True
        
        def digest(self, tokens):
            for tok in tokens:
                if tok.isElementContentWhitespace:
                    continue
                tokens.push(tok)
                break
            self.digestUntil(tokens, metadata._metacmd)
            if self.forcePars:
                self.paragraphs()
    
    class author(_metacmd): pass
    class creationdate(_metacmd): pass
    class difficulty(_metacmd): pass
    class itemtype(_metacmd): pass
    class status(_metacmd): pass
    class time(_metacmd): pass
    
#
# Environments specifying items and quizes
#
class itembody(Environment):
    args = 'content'

#
# multiplechoice/truefalse and other environments
#
class _env(Base.List):
    class _item(Base.List.item):
        forcePars = True
  
    class choice(_item):
        args = '[ term ] content'

    class explanation(_item):
        args = ''

    class solution(_item):
        args = ''

class truefalse(_env):
    args = 'content'

class multiplechoice(_env):
    args = 'content'

