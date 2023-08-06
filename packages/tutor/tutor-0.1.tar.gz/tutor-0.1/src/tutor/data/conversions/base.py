#-*- coding: utf-8 -*-W
from tutor.util import jsonlib
import os
import tempfile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

#===============================================================================
#                             Importing
#===============================================================================
class Import(object):
    '''
    An Import instance reads a file/string and return a JSON-like structure
    equivalent to the file. 

    This is the base class for all importers and it does not implement anything.
    '''
    def load(self, file, type):
        '''
        Load JSON object from file of a given type.
        
        This method simply dispatches the work to the other load_* and loads_* 
        methods in this class.
        
        Arguments
        ---------
        file : file-like object
            Buffer object holding data.
        type : str
            Type of data in file object
        '''

        # Tries to use the load_type method
        try:
            func = getattr(self, 'load_' + type)
        except AttributeError:
            pass
        else:
            return func(file)

        # Now, tries to use the loads_type method
        try:
            func = getattr(self, 'loads_' + type)
        except AttributeError:
            raise ValueError("unsupported type, '%s'" % type)
        else:
            return func(file.read())

    def loads(self, st, type):
        '''
        Similar to load(), but the input is a string rather than a file object. 
        '''
        with StringIO(st) as F:
            return self.load(F, type, file)

    # Automatic loaders --------------------------------------------------------
    def loads_json(self, st):
        '''
        De-serialize a JSON object.
        '''
        return jsonlib.loads(st)

    def load_lyx(self, file):
        '''
        This method uses the LaTeX loader as an intermediate step for loading 
        the LyX file. 
        '''

        try:
            latex_loader = getattr(self, 'load_tex')
        except AttributeError:
            raise RuntimeError('cannot load LyX file because LaTeX is not accepted')

        # Copy data to a known location
        tmpfile = tempfile.NamedTemporaryFile(suffix='.lyx')
        tmpfile.write(file.read())
        tmpfile.flush()
        fpath = tmpfile.name

        # Convert to TeX using LyX in the command-line
        cmd = 'lyx -f -e latex "%s"' % fpath
        localdir = os.getcwd()
        try:
            try:
                os.chdir(os.path.dirname(fpath))
                os.system(cmd)
                texpath = fpath[:-3] + 'tex'
                with open(texpath) as F:
                    texdata = F.read()
                    texdata = StringIO(texdata)
            finally:
                # Delete tex, lyx and lyx~ files
                os.remove(texpath)
                try:
                    os.remove(fpath + '~')
                except OSError:
                    pass
        finally:
            os.chdir(localdir)

        # Uses a LaTeX loader to process data
        return latex_loader(texdata)

#===============================================================================
#                             Exporting
#===============================================================================
class Export(object):
    #TODO: implement some exporting interface
    def dump(self, json_obj, type, out_file):
        '''
        Convert the JSON object to data stream of a given type and dumps it in
        out_file.
        
        This method dispatches the work to the other dump_* and dumps_* methods
        in this class.
        
        Arguments
        ---------
        json_obj : JSON-like structure
            JSON representation of object.
        type : str
            Type of data in the JSON structure
        out_file : writable file-like object
            File used to dump data in 
        '''
        # Tries to use the dump_type methods
        try:
            func = getattr(self, 'dump_' + type)
        except AttributeError:
            pass
        else:
            func(json_obj, out_file)

        # Now, tries to use the dumps_type methods
        try:
            func = getattr(self, 'dumps_' + type)
        except AttributeError:
            pass
        else:
            data = func(json_obj)
            out_file.write(data)

    def dumps(self, json_obj, type):
        '''
        Similar to dump(), but does not accept an output file as argument. 
        Rather, this function returns a string of data.
        '''

        with StringIO() as F:
            self.dump(json_obj, type, F)
            return F.getvalue()

    def dumps_json(self, json_obj):
        '''
        Return a string representing the json object. 
        '''
        return jsonlib.dumps(json_obj)

#===============================================================================
#                              Parsing
#===============================================================================
class Parser(object):
    '''
    This is the base class of all parsers.
    '''
    def __init__(self, file):
        self.file = file

    def parse(self):
        raise NotImplementedError

#===============================================================================
#                            Cooperative functions
#===============================================================================
#TODO: put these classes in somewhere sensible inside tutor.util or chipslib
class request(object):
    "Represents a co-function's request for getting output"
    def __init__(self, signal):
        self.signal = signal
    def __str__(self):
        if isinstance(self.signal, basestring):
            signal = self.signal
        else:
            signal = type(self.signal)
        return 'request(%s)' % signal

class push(object):
    "Represents a co-function's request for sending input"
    def __init__(self, signal, data):
        self.signal = signal
        self.data = data

    def __str__(self):
        if isinstance(self.data, basestring):
            data = self.data
        else:
            data = type(self.data)
        return 'push(%s, %s)' % (self.signal, data)

class cooperative(object):
    def __init__(self, iterator):
        "Class that controls signals and iteration in cooperative functions"
        self.iter = iter(iterator)

    def send(self, signal, data):
        'Sends data marked as signal to a collaborator function.'
        for msg in self.iter:
            if isinstance(msg, request) and msg.signal == signal:
                self.iter.send(data)
                break

    def get(self, signal):
        'Returns data when collaborator issues a given signal'
        for msg in self.iter:
            if isinstance(msg, push) and msg.signal == signal:
                return msg.data

    def finish(self):
        "Finshes collaborator's execution and return the result"
        for ret in self.iter:
            pass
        return ret

    def __iter__(self):
        return self

    def next(self):
        return self.iter.next()
