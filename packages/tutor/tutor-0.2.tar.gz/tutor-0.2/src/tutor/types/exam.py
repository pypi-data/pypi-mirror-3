import random
from datetime import datetime
import tutor.version
from tutor.history import History
from tutor.util import rand_id
from tutor.types.schema import sch_instance, Str, Opt, SchemaObj, Array, Datetime, Number
from tutor.types.question import Question
from tutor.types.pool_view import PoolView

class ExamPool(SchemaObj):
    '''
    Represents groups of Exam objects organized in different sequential 
    revisions. ExamPool objects can store references to QuestionPool objects or
    the entire objects themselves.
    
    Actual exams can be retrieved using a index notation from a ExamPool object
    using a  (revision_no, revision_key) tuple:
    
    >>> expool = ExamPool('foo')
    >>> expool.commit(10)
    
    First object of the last revision
    
    >>> expool[-1, 0] #doctest: +ELLIPSIS 
    <...Exam object at 0x...>
       
    '''
    class schema(sch_instance):
        id = Str() #@ReservedAssignment
        name = Str()
        title = Str()
        subtitle = Str('')
        author = Str()
        version = Str()
        ctime = Datetime()
        value = Number(1.0)
        comment = Opt(Str())
        history = Array()
        questions = Array()

    def __init__(self, name, id=None, author='<no author>', title='<untitled>', subtitle=None, #@ReservedAssignment
                 ctime=None, comment=''):
        '''Creates a new empty exam. 
        
        Parameters
        ----------
        name : str
            Name for the new exam.
        exam_id : str
            The exam id can be set manually, if required.
            
        Examples
        --------
        
        >>> exm = ExamPool('foo')
        >>> exm.name, exm.title  
        (u'foo', u'<untitled>')
        
        Each exam is represented internally as a sequence of question numbers. 
        The revision also contains a 'template' object that is a sequence
        with (question id, question revision)  
        '''
        super(ExamPool, self).__init__()

        self.id = id or rand_id('exam')
        self.name = unicode(name)
        self.title = unicode(title)
        self.author = unicode(author)
        self.ctime = ctime if ctime is not None else datetime.now()
        self.comment = unicode(comment)
        self.history = History()
        self.questions = []
        self.version = tutor.version.VERSION
        self.commit(0, final=False)

    def add_question(self, *args, **kwds):
        '''Adds a question to an exam.'''

        force = kwds.get('force', False)
        for qst in args:
            qst_ids = set(q.id for q in self.questions)
            q_id = qst.id
            if force or q_id not in qst_ids:
                self.questions.append(qst)
            else:
                raise ValueError('question already present in exam')

    def update_question(self, qst):
        '''Updates a question to the exam'''

        ids = [q.id for q in self.questions]
        idx = 0
        while True:
            try:
                idx = ids.index(qst.id, idx)
                self.questions[idx] = qst
            except ValueError:
                if not idx:
                    raise ValueError('question "%s" not in ExamPool' % qst.id)
                else:
                    break

    def commit(self, size=100, final=True, ammend=False):
        '''Creates ``size`` new versions of the exam from the template'''

        questions = self.questions
        revision = {}
        revision['template'] = [(q.id, q.history.last.id) for q in questions ]
        revision['final'] = final

        # Revision sizes
        q_rev_sizes = [sum(1 for k in q.history.last.keys() if k.isdigit())
                    for q in questions]

        if 0 in q_rev_sizes:
            bad_idx = q_rev_sizes.index(0)
            bad_qst = self.questions[bad_idx]
            q_id, q_rev = bad_qst.id, bad_qst.history.last.id
            raise ValueError('revision %s of question %s (%s) is empty' % (q_rev, q_id, bad_qst.name))

        # Save exams in revision
        for idx in range(size):
            exam = [ str(random.randrange(s)) for s in q_rev_sizes ]
            revision[str(idx)] = exam

        if self.history and not getattr(self.history[-1], 'final', True):
            self.history.pop()
        self.history.new_revision().update(revision)

#    def question_bodies(self, path=None, revision=None):
#        '''
#        Get a list with the body of all questions for the given exam.
#        
#        This method can be called in many different ways.
#        
#        The first argument can be a list or a path string, which is interpreted
#        as either 'exam_id::revision::exam_no', or as 'revision::exam_no'. In 
#        both cases, the user cannot set the 'revision' keyword. 
#        
#        The method can also be called as `obj.question_bodies(key [, revision])`, 
#        in which ``key`` can be an integer index or the string "template". 
#        ``revision`` defaults to the last revision.
#        
#        Examples
#        --------
#        
#        Creates a new  exam and add some questions
#        
#        >>> from tutor.types.question import QuestionPool
#        >>> exm = ExamPool('foo')
#        >>> qst_list = [ QuestionPool(name) for name in ['ham', 'spam', 'eggs']]
#        >>> for qst in qst_list: 
#        ...     qst.commit(10)
#        ...     exm.add_question(qst)
#        >>> exm.commit(10)
#        
#        We can retrieve the question bodies in many different ways.
#        
#        The first commit from the last revision:
#        
#        >>> exm.question_bodies(0) # doctest: +ELLIPSIS
#        [(<...QuestionPool object at 0x...>, [<...>]), ..., (..., ...)]
#        
#        One can use the partial path in the form "revision::body_no"
#        
#        >>> exm.question_bodies('%s::%s' % (exm.history.last.id, '0')) # doctest: +ELLIPSIS
#        [(<...QuestionPool object at 0x...>, [<...>]), ..., (..., ...)]
#        
#        Or the full path "exam::revision::body_no"
#        
#        >>> exm.question_bodies('%s::%s::%s' % (exm.id, exm.history.last.id, '0')) # doctest: +ELLIPSIS
#        [(<...QuestionPool object at 0x...>, [<...>]), ..., (..., ...)]
#        
#        '''
#        if isinstance(path, basestring):
#            spath = path.split('::')
#            if len(spath) == 1:
#                if path != 'template':
#                    raise ValueError('invalid path: %s' % path)
#                else:
#                    key = path
#            elif len(spath) == 2:
#                rev, key = spath
#            elif len(spath) == 3:
#                exm, rev, key = spath
#                if exm != self.id:
#                    raise ValueError('wrong exam: expecting %s, but got %s' % (exm, self.id))
#            else:
#                raise ValueError('invalid path: %s' % path)
#
#            revision = self.history[rev]
#        else:
#            revision = self.history[revision if revision is not None else -1]
#            key = unicode(path)
#
#        questions = [ (self[qst]) for (qst, rev) in revision['template'] ]
#        qst_revisions = \
#            [ (self[qst].history[rev]) for (qst, rev) in revision['template'] ]
#        exam_template = revision[key]
#        bodies = [ rev[k] for (k, rev) in zip(exam_template, qst_revisions) ]
#        return list(zip(questions, bodies))

    # Magic methods ------------------------------------------------------------
    def __getitem__(self, key):
        rev_no, rev_key = key
        return Exam(self, rev_no, rev_key)

    def question(self, question_id):
        '''Return a question from its id'''

        for qst in self.questions:
            if qst.id == question_id:
                return qst
        else:
            raise ValueError("question '%s' not found" % question_id)

    def iterexams(self, revision):
        '''Iterates over all exams'''

        for k in self.history[revision]:
            idx, _, __ = k.partition('-')
            if idx.isdigit():
                yield self[revision, idx]

    def exams(self, revision):
        '''List with all exams'''

        return list(self.iterexams())

class Exam(PoolView):
    def __init__(self, pool, rev_no, rev_key):
        super(Exam, self).__init__(pool, rev_no, rev_key)
        self.parent = pool
        questions = self.body = []
        body = pool.history[self._revision_no][self._revision_key]
        template = pool.history[self._revision_no]['template']
        for key, (qst, rev) in zip(body, template):
            qpool = pool.question(qst)
            question = Question(qpool, rev, key)
            question.parent = self
            questions.append(question)

    @property
    def subtitle(self):
        return self._pool.subtitle

    # Relations ----------------------------------------------------------------
    children = Question.parent.symmetrical
    #parent = ManyToOne()

    def __getitem__(self, idx):
        return self.body[idx]

    def question(self, idx):
        return self.body[idx]


if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)


