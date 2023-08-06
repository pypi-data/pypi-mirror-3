import sys
import contextlib

class stringfile(bytearray):
    '''A bytearray that also works like a file.'''

    def __init__(self, data='', encoding=None):
        super(stringfile, self).__init__(data)
        self.closed = False
        self.encoding = encoding
        self.curr = 0

    # Default values -----------------------------------------------------------
    name = '<string>'
    errors = ()
    mode = 'w'

    # File API -----------------------------------------------------------------
    def close(self):
        self.closed = True

    def fileno(self):
        raise OSError('not a OS file')

    def flush(self):
        pass

    def isatty(self):
        return False

    def next(self): #@ReservedAssignment
        try:
            result = self[self.curr]
        except IndexError:
            raise StopIteration
        self.curr += 1
        return result

    def __iter__(self):
        return self

    def iterchars(self):
        return super(stringfile, self).__iter__()

    def read(self, size=None):
        final = self.curr + (size if size is not None else len(self))
        final = min(final, len(self))
        result = str(self[self.curr:size])
        self.curr = final
        return result

    def readline(self, size=None):
        raise NotImplementedError

    def readlines(self, size=None):
        raise NotImplementedError

    def seek(self, offset, whence=0):
        raise NotImplementedError

    def tell(self):
        return self.curr

    def truncate(self, size):
        raise NotImplementedError

    def write(self, data=''):
        if isinstance(data, unicode):
            data = data.encode(self.encoding)
        padding = len(data) - (len(self) - self.curr)
        if padding > 0:
            self.extend(['\x00' for _ in range(padding)])
        self[self.curr:self.curr + len(data)] = data
        self.curr += len(data)

    def writelines(self, seq):
        for st in seq:
            self.write(st)

    def encode(self, encoding=None):
        raise NotImplementedError

    def decode(self, encoding=None):
        raise NotImplementedError

@contextlib.contextmanager
def grab_output(errors=False, encoding=None):
    '''Redirects standard output data to the returning bytearray.
    
    If errors is True, also redirects sys.stderr.'''

    data = stringfile(encoding=encoding)
    old = sys.stderr, sys.stdout
    sys.stdout = data

    if errors:
        sys.stderr = data

    try:
        yield data
    finally:
        sys.stderr, sys.stdout = old

if __name__ == '__main__':
    with grab_output() as data:
        print 'foo'
        print 'bar'
    print data

