from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.types' #@ReservedAssignment
    import tutor.types #@UnusedImport

from decimal import Decimal
import datetime
from .schema import SchemaObj, sch_instance, Opt, Str, Anything, Number, Array, Datetime, Dict
from ..util.rand_id import rand_id
from ..util import relational

__all__ = ['Response', 'Unreadable', 'Empty', 'RawScore', 'Cancelled', 'ResponseSeq', 'ResponsePool']

class Response(SchemaObj):
    '''Represents a response to a SubQuestion.
    
    Parameters
    ----------
    obj : SubQuestion
        SubQuestion object that is subject of the response.
    data : anything
        Arbitrary Python data expected by the obj.score(data) function.
    score : numeric
        The score assigned to the question. If not given, it is computed from
        the data object.
    value : numeric
        Value assigned to the question. It is normally computed from `obj`, but
        it may be set to null or some other value (e.g., a cancelled question).
    ctime : datetime
        Creation time for the response object.
    
    Additional keyword arguments are added to a dictionary with arbitrary meta 
    information about the question (e.g., name and credentials of the grader 
    user, method used to grade it, etc).
    '''

    class schema(sch_instance):
        objref = Array()
        student_id = Opt(Str())
        data = Opt(Anything())
        score = Opt(Number())
        value = Opt(Number())
        ctime = Datetime()
        meta = Dict({})

    def __init__(self, obj, data=None, score=None, value=None, ctime=None, student_id=None, **kwds):
        ctime = ctime if ctime is not None else datetime.datetime.now()
        value = Decimal(value) if value is not None else Decimal(obj.value)
        if data is None and type(self) is Response:
            raise ValueError("'Response' object with null data")
        if score is not None:
            score = Decimal(str(score))
        super(Response, self).__init__(objref=obj.ref, value=value, data=data, score=score, meta=kwds, ctime=ctime, student_id=student_id)
        if score is not None and not (0 <= score <= 1):
            raise ValueError('score must be normalized between 0 and 1')
        self._process_object(obj)

    def _process_object(self, obj):
        '''Compute score from object, when necessary.'''

        if self.score is None:
            score = obj.score(self) / self.value
            if 0 <= score <= 1:
                self.score = score
                #self.feedback = obj.feedback(self.data)
            else:
                raise ValueError('score must be between 0 and 1, got %s' % score)

    @property
    def raw_score(self):
        return self.value * self.score

    def __getattr__(self, attr):
        try:
            return self.meta[attr]
        except KeyError:
            raise AttributeError(attr)

    parent = relational.ManyToOne()

class NoResponse(Response):
    '''Response object associated with sub-questions that do not have a 
    score.'''

    def __init__(self, obj, **kwds):
        super(NoResponse, self).__init__(obj, None, None, None, None, **kwds)

class Empty(Response):
    '''Student did not responded to question'''

    def __init__(self, obj, **kwds):
        super(Empty, self).__init__(obj, None, 0, None, None, **kwds)

class Unreadable(Response):
    def __init__(self, obj, **kwds):
        super(Empty, self).__init__(obj, None, 0, None, None, **kwds)

class RawScore(Response):
    '''Represents a manual score given by the teacher/tutor.'''

    def __init__(self, obj, score, **kwds):
        super(RawScore, self).__init__(obj, None, score, None, None, **kwds)

class Cancelled(Response):
    '''A cancelled question.'''

    def __init__(self, obj, score=0, **kwds):
        value = score * obj.value
        super(RawScore, self).__init__(obj, None, score, value, None, **kwds)

class ResponseSeq(Response):
    '''Represents the response to a question or exam.
    
    A question consists of a list of subquestions. Likewise, the data section 
    of a question consists of a list of Response objects of each subquestion.
    '''
    def __init__(self, obj, data=None, score=None, value=None, ctime=None, **kwds):
        # fill in sub-responses
        try:
            data_ref = {resp.objref: resp for resp in data}
        except TypeError:
            pass
        else:
            data = []
            for sub in obj:
                ref = sub.ref
                try:
                    data.append(data_ref[ref])
                except KeyError:
                    data.append(Empty(sub))

        super(ResponseSeq, self).__init__(obj, data, score, value, ctime, **kwds)

    def __getitem__(self, sub):
        if self.data is None:
            raise KeyError('empty responses')
        for subresp in self.data:
            if subresp.objref == sub.ref:
                return subresp
        else:
            raise KeyError(sub)

class ResponsePool(SchemaObj):
    '''Represents a group of responses for a given QuestionPool or ExamPool 
    object.
    '''
    class schema(sch_instance):
        id = Str()
        pool_id = Str()
        pool_rev = Str()
        responses = Array()
        ctime = Datetime()

    def __init__(self, pool_id, pool_rev, ctime=None):
        super(ResponsePool, self).__init__()
        self.id = rand_id(10)
        self.pool_id = getattr(pool_id, 'id', pool_id)
        self.pool_rev = pool_rev
        if not ctime:
            ctime = datetime.datetime.now()
        self.ctime = ctime
        self.responses = []

    def fromstudent(self, student_id, single=False):
        '''Return a list of responses given by the student with the given id'''
        pass

    def addresponse(self, response):
        self.responses.append(response)

if __name__ == '__main__':
    from ..examples import new_exam
    exm = new_exam(commit=10)[-1, 0]

    import time
    t0 = time.time()
    resps = [ q[0].response([q[0].order[0]]) for q in exm ]
    qresps = [ q.response([r]) for r in resps ]
    eresp = exm.response(qresps)
    print([ (r.score, r.value) for r in resps ])
    print([ (r.score, r.value) for r in qresps ])
    print(eresp)
    print(eresp.dictview)
    print(t0 - time.time())

    import doctest
    doctest.testmod()
