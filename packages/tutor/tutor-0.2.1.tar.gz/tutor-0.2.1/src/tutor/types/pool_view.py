import weakref
import collections
from decimal import Decimal
from .response import ResponseSeq

class PoolView(collections.MutableSequence):
    '''Generic pool view objects for presenting QuestionPool or ExamPool 
    objects 
    '''
    _OBJECTS = weakref.WeakValueDictionary()

    def __new__(cls, pool, rev_no, rev_key):
        rev_no = pool.history.index(pool.history[rev_no])
        rev_key = unicode(rev_key)
        pool_id = id(pool)
        try:
            return cls._OBJECTS[(pool_id, rev_no, rev_key)]
        except KeyError:
            new = object.__new__(cls)
            new._pool = pool
            new._revision_no = rev_no
            new._revision_key = rev_key
            cls._OBJECTS[(pool_id, rev_no, rev_key)] = new
            return new

    def __init__(self, pool, rev_no, rev_key):
        pass

    @property
    def id(self): #@ReservedAssignment
        return self._pool.id

    @property
    def revision_id(self):
        return self._pool.history[self._revision_no].id

    @property
    def revision_key(self):
        return self._revision_key

    @property
    def ref(self):
        return (self.id, self.revision_id, self.revision_key)

    @property
    def name(self):
        return self._pool.name

    @property
    def title(self):
        return self._pool.title

    @property
    def author(self):
        return self._pool.author

    @property
    def version(self):
        return self._pool.version

    @property
    def ctime(self):
        return self._pool.ctime

    @property
    def value(self):
        return self._pool.value

    @property
    def comment(self):
        return self._pool.comment

    @property
    def template(self):
        return type(self)(self._pool, self._revision_no, 'template')

    @property
    def pool(self):
        return self._pool

    #===========================================================================
    # Abstract methods
    #===========================================================================
    def __getitem__(self, idx):
        return self.body[idx]

    def __len__(self):
        return len(self.body)

    def __setitem__(self, idx, value):
        raise NotImplementedError
        value.parent = self
        self.body[idx] = value

    def __delitem__(self, idx):
        raise NotImplementedError

    def insert(self, idx, value):
        raise NotImplementedError

    #===========================================================================
    # Responses
    #===========================================================================
    def score(self, response):
        '''Compute score (between 0 and 1) corresponding to the given response'''

        scores = [(subr.score or 0) for subr in response.data]
        values = [(subr.value or 0) for subr in response.data]
        return Decimal(sum(s * v for (s, v) in zip(scores, values))) / Decimal(sum(values))

    def response(self, sub_responses, **kwds):
        '''Returns a new MultiResponse object from the list of sub-responses'''

        return ResponseSeq(self, sub_responses, **kwds)

