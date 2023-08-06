import fs.errors
from fs.tempfs import TempFS
import pyson
from pyson.json_encoding import register_cls
from tutor.util.fs_util import fsitems

@register_cls('tutor.SrcFolder')
class SrcFolder(TempFS):
    '''
    A file structure representing the src/ directory of a Question object. 
   
    SrcData() has methods for searching for the main and namespace files inside
    the src directory. SrcData objects can also be serialized in JSON.
    
    Examples
    -------- 
    >>> src = SrcFolder()
    >>> with src.open('main.lyx', 'w') as F:
    ...     F.write('<template data>')
    
    One can access the path and type of main file
    
    >>> src.main_path, src.main_t
    (u'main.lyx', u'lyx')
    
    Or open it to read or write
    
    >>> with src.open_main() as F:
    ...     print F.read()
    <template data>
    
    The special files can be created and open after setting their type 
    
    >>> with src.open_namespace(type='py') as F:
    ...     F.write('<namespace data>')
    >>> src.namespace_path
    u'namespace.py'
    '''
    MAIN_PRIORITY = {'tex': 1, 'lyx':2}
    NAMESPACE_PRIORITY = {'py': 1}

    def __init__(self):
        super(SrcFolder, self).__init__()
        self.makedir('media')
        self.makedir('aux')

    def _fgetter(self, fname, priority, idx):
        # implements the main_t, namespace_t, main_path and namespace_path
        N = len(fname)
        fpaths = (p for p in self.listdir() if p.startswith(fname))
        fpaths = ((p[N:], p) for p in fpaths)
        fpaths = list((priority.get(ext, 0), ext, p) for (ext, p) in fpaths)
        fpaths.sort()
        try:
            if fpaths:
                return fpaths[-1][idx]
            else:
                return None
        except IndexError:
            return None

    @property
    def main_t(self):
        return self._fgetter('main.', self.MAIN_PRIORITY, 1)

    @property
    def namespace_t(self):
        return self._fgetter('namespace.', self.NAMESPACE_PRIORITY, 1)

    @property
    def main_path(self):
        return self._fgetter('main.', self.MAIN_PRIORITY, 2)

    @property
    def namespace_path(self):
        return self._fgetter('namespace.', self.NAMESPACE_PRIORITY, 2)

    def _opener(self, tt, mode, ext):
        # implements open_main and open_namespace
        if ext is not None:
            if mode is not None:
                raise ValueError("can only set 'mode' and 'ext' simultaneously")
            else:
                return self.open('%s.' % tt + ext, 'w')
        else:
            ext = getattr(self, tt + '_t')
            mode = mode if mode is not None else 'r'
            try:
                return self.open('%s.' % tt + ext, mode)
            except TypeError:
                raise fs.errors.ResourceNotFoundError('no %s file!' % tt)

    def open_main(self, mode=None, type=None):
        '''Return a file object with the main file.'''

        return self._opener('main', mode, type)

    def open_namespace(self, mode=None, type=None):
        '''Return a file object with the namespace file.'''

        return self._opener('namespace', mode, type)

    #===========================================================================
    # JSON conversion
    #===========================================================================
    def _json_encode_(self):
        json = {}
        for k, v in fsitems(self):
            json[k] = v.read().encode('base64')
            v.close()
        return json

    @classmethod
    def _json_decode_(cls, json):
        new = cls()
        for k, v in json.items():
            with new.open(k, 'w') as F:
                F.write(v.decode('base64'))
        return new

    def __eq__(self, other):
        if isinstance(other, SrcFolder):
            json1 = pyson.json_encode(self)
            json2 = pyson.json_encode(other)
            return not any(pyson.walkdiff(json1, json2))
        else:
            return False

    def __ne__(self, other):
        return not self == other

if __name__ == '__main__':
    src = SrcFolder()
    src.makeopendir('foo/bar', True)
    with src.open('foo/bar/foobar', 'w') as F:
        F.write('sfdds sdjfo sdjfs')

    pyson.sprint(pyson.json_encode(src))

    print SrcFolder.mro()
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)



