import os
import datetime
from tutor.config.settings import SYSTEM_LIB

class Addr(object):
    def __init__(self, path, sep=None, base=''):
        if sep is None:
            self.sep = os.path.sep
        else:
            self.sep = str(sep)
        self._full_path = path.split(self.sep)
        self.addr = path

        base = os.path.join(SYSTEM_LIB, base)
        if not base:
            self._base = []
        else:
            if base.endswith(self.sep):
                base = base[:-len(self.sep)]
            self._base = base.split(self.sep)

    # Properties ---------------------------------------------------------------
    @property
    def full_path(self):
        return self.sep.join(self._base + self._full_path)

    @property
    def path(self):
        return self.sep.join(self._full_path)

    @property
    def base(self):
        return self.sep.join(self._base)

    @property
    def basedir(self):
        return self.sep.join(self._base + self._full_path[:-1])

    @property
    def name(self):
        return self._full_path[-1]

    # os.path API --------------------------------------------------------------
    def join(self, *args):
        '''
        Append one or more pathname components, inserting path separator as 
        needed.
        '''
        for arg in args:
            for p in arg.split(self.sep):
                self._full_path.append(p)

    # Locate important files related to addr -----------------------------------
    def _files(self):
        name = self.name
        files = os.listdir(self.basedir)
        return set([ f for f in files if f.startswith(name) ])

    def _data_path(self):
        name = self.name
        files = self._files()
        for ext in '.view.xml .view.tex .view.lyx .xml .tex .lyx .cvs .json'.split():
            if name + ext in files:
                return self.full_path + ext

    def get_data(self):
        '''
        Returns a file object holding data at the given addr.
        
        Example
        -------
        
        >>> addr = Addr('examples/lyx_simple', base='learning_obj')
        >>> print addr.get_data().read() #doctest: +ELLIPSIS
        #LyX ... created this file. For more info see ...
        ...
        \end_document
        <BLANKLINE>
        
        '''
        path = self._data_path()
        if path is None:
            raise IOError('invalid addr, ' + self.addr)
        return open(path)

    def get_data_type(self):
        '''
        Returns the data type (as given by the file extension).
        
        Example
        -------
        
        >>> addr = Addr('examples/lyx_simple', base='learning_obj')
        >>> print addr.get_data_type()
        lyx
        '''

        return os.path.splitext(self._data_path())[1][1:]

    def has_aux(self):
        '''
        Returns True if address uses auxiliary data besides Addr.get_data().
        
        Example
        -------
        
        >>> addr = Addr('examples/lyx_simple', base='learning_obj')
        >>> print addr.has_aux()
        False
        '''
        path = self._data_path()
        postfix = path[len(self.full_path):]
        return postfix.startswith('.view')

    def get_main_aux(self):
        name = self.name
        files = self._files()
        for ext in '.py .yaml .pool.xml'.split():
            if name + ext in files:
                return (ext[1:], open(self.full_path + ext))

    def get_all_aux(self):
        pass

    def get_mtime(self):
        files = self._files()
        time = os.path.getmtime
        basedir = self.basedir
        join = os.path.join
        mean_mtime = sum(time(join(basedir, f)) for f in files) / len(files)
        return datetime.datetime.fromtimestamp(mean_mtime)

    def exists(self):
        return bool(self._data_path())

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
