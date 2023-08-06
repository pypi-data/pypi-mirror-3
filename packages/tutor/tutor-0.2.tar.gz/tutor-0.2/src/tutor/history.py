import datetime
import collections
import contextlib
import pyson
from pyson.json_encoding import register_cls
from tutor.util import rand_id

@register_cls('tutor.History')
class History(collections.MutableSequence, list):
    '''Represents a linear sequence of revisions.
    
    Examples
    --------
    
    >>> history = History()
    >>> rev = history.new_revision(id='my_rev')
    >>> rev.update(foo='foo data', bar='bar data')
    
    History is very similar to a list of revisions.
    
    >>> history.append(Revision()); len(history)
    2
    >>> list(history) # doctest: +ELLIPSIS
    [<Revision "my_rev" (2 items)>, <Revision "..." (0 items)>]
    
    One can access objects in the history using the path formed as 
    ('revision', 'key'). 
    
    >>> history['my_rev', 'foo']
    'foo data'
    
    Setting values also work. The 'last' revision can be accessed using the
    special keyword 'last'.
    
    >>> history['last', 'ham'] = 'spam'
    >>> history.last.items()
    [('ham', 'spam')]
    
    '''
    __slots__ = []

    def index_from_id(self, rev_id):
        if rev_id == 'last':
            return len(self) - 1
        for idx, rev in enumerate(self):
            if rev.id == rev_id:
                return idx
        else:
            raise KeyError('not found: %s' % rev_id)

    def id_list(self):
        '''Return a list of ids in self'''

        return [ rev.id for rev in self ]

    def new_revision(self, **kwds):
        '''Creates a new revision'''

        revision = Revision(parent=self.last, **kwds)
        self.append(revision)
        return revision

    @property
    def last(self):
        try:
            return self[-1]
        except IndexError:
            return None

    def deepcopy(self):
        '''Return a deep copy of History object. Shallow copies can be created
        easily using the slice syntax, e.g.: obj[:] --> copy of obj.'''

        # Fix parents
        return History(obj.copy() for obj in self)

    #===========================================================================
    # Mixin methods
    #===========================================================================
    @contextlib.contextmanager
    def _safe_insert(self, obj, other):
        if obj is other or obj == other:
            yield
        else:
            # Assert compatibility
            if not isinstance(obj, Revision):
                raise TypeError('can only insert Revision objects, got %s' % type(obj))
            if obj.id is not None:
                if obj.id in set(self.id_list()):
                    raise ValueError('revision with repeated id, %s' % obj.id)

            # Begin with block
            try:
                yield

            # Finalize
            finally:
                if obj.id is None:
                    obj.reset_id()
                    ids = set(self.id_list())
                    while obj.id in ids:
                        obj.reset_id()

    def _path_sep(self, path):
        if isinstance(path, int):
            return path

        elif isinstance(path, basestring):
            return self.index_from_id(path)

        elif isinstance(path, tuple):
            rev_id, key = path
            return self.index_from_id(rev_id), key

        else:
            raise TypeError('paths must be strings, ints or tuples, got: %s' % type(path))

    def __len__(self):
        return list.__len__(self)

    def __getitem__(self, idx):
        path = self._path_sep(idx)
        if isinstance(path, int):
            return list.__getitem__(self, path)
        else:
            idx, key = path
            return self[idx][key]

    def __delitem__(self, idx):
        path = self._path_sep(idx)
        try:
            list.__delitem__(self, idx)
        except TypeError:
            idx, key = path
            del self[idx][key]

    def __setitem__(self, idx, value):
        path = self._path_sep(idx)
        if isinstance(path, tuple):
            idx, key = path
            self[idx][key] = value
        else:
            with self._safe_insert(value, self[idx]):
                list.__setitem__(self, idx, value)

    def insert(self, idx, value):
        path = self._path_sep(idx)
        if isinstance(path, int):
            with self._safe_insert(value, None):
                list.insert(self, idx, value)
        else:
            raise ValueError('cannot insert values in revision')

    # who is first in mro()
    __iter__ = list.__iter__
    index = list.index
    #===========================================================================
    # JSON conversion
    #===========================================================================
    def __json_encode__(self):
        return [ Revision.__json_encode__(x) for x in self ]

    @classmethod
    def __json_decode__(cls, obj):
        new = cls()
        for rev in obj:
            rev = pyson.json_decode(rev, Revision)
            rev.parent = new.last
            new.append(rev)
        return new

@register_cls('tutor.Revision')
class Revision(dict):
    '''
    Revision objects are a mapping between names and objects. They work like
    dictionaries, but have some additional meta information.
    
    It is possible to access previous versions of a key using a special notation:
    
    >>> rev1 = Revision({'spam': 'eggs'})
    >>> rev2 = Revision({'spam': 'ham'}, parent=rev1)
    >>> rev2['spam']
    'ham'
    >>> rev2['spam', -1]
    'eggs'
    '''
    __slots__ = ['parent', 'id', 'ctime', 'meta']

    def __init__(self, data=None, parent=None, id=None, ctime=None, **kwds):
        super(Revision, self).__init__(data if data is not None else {})
        self.parent = parent
        self.id = id
        self.ctime = ctime if ctime else datetime.datetime.now()
        self.meta = dict(kwds)

    def reset_id(self):
        '''Sets "id" to a randomized value.'''
        self.id = rand_id('revision')

    def copy(self, keep_parent=True):
        copy = super(Revision, self).copy()
        copy.parent = self.parent if keep_parent else None
        copy.id = self.id
        copy.ctime = self.ctime
        copy.meta = self.meta.copy()
        return copy

    #===========================================================================
    # Magic methods
    #===========================================================================
    def __getattr__(self, attr):
        try:
            return self.meta[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        if attr in self.__slots__:
            super(Revision, self).__setattr__(attr, value)
        else:
            self.meta[attr] = value

    def __str__(self):
        return '<Revision "%s" (%s items)>' % (self.id, len(self))

    def __getitem__(self, key):
        if isinstance(key, tuple):
            key, idx = key
            if idx == 0:
                return super(Revision, self).__getitem__(key)
            elif idx < 0:
                return self.parent[key, idx + 1]
            else:
                raise ValueError('indexes must be negative!')
        else:
            return super(Revision, self).__getitem__(key)

    __repr__ = __str__

    @property
    def parent_id(self):
        if self.parent is None:
            return None
        else:
            return self.parent.id

    def iteritems(self, sort=False):
        if sort:
            return ((k, self[k]) for k in self.iterkeys(True))
        else:
            return super(Revision, self).iteritems()

    def iterkeys(self, sort=False):
        if sort:
            keys = map(splitdigits, self.keys())
            head = sorted((idx, data, k) for ((idx, data), k) in zip(keys, self.keys()) if idx is not None)
            head = [k for (idx, data, k) in head]
            tail = sorted((idx, data, k) for ((idx, data), k) in zip(keys, self.keys()) if idx is None)
            tail = [k for (idx, data, k) in tail]
            return iter(head + tail)
        else:
            return super(Revision, self).iterkeys()

    def itervalues(self, sort=False):
        if sort:
            return (self[k] for k in self.iterkeys(True))
        else:
            return super(Revision, self).itervalues()

    def items(self, sort=False):
        return list(self.iteritems(sort))

    def keys(self, sort=False):
        return list(self.iterkeys(sort))

    def values(self, sort=False):
        return list(self.itervalues(sort))

    #===========================================================================
    # JSON conversion
    #===========================================================================
    def __json_encode__(self):
        return dict(ctime=self.ctime, parent=self.parent_id, id=self.id, data=dict(self), meta=self.meta)

    @classmethod
    def __json_decode__(cls, obj):
        return cls(**obj)

def splitdigits(st):
    '''For a string that may start with digits, returns a tuple (int, data)
    separating the digits from character parts. If the string does not start
    with a digit, it returns (None, str)'''

    digits = []
    while st and st[0].isdigit():
        digits.append(st[0])
        st = st[1:]
    if digits:
        return int(''.join(digits)), st
    else:
        return None, st

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)

