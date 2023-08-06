#-*- coding: utf8 -*-
from propertylib import oncedescriptor
import itertools
import pyson
from tutor.types.response import Empty, RawScore, ResponseSeq
from tutor.plugins.email import Inbox, Outbox
from tutor.util.fs_util import SavingFS
from tutor.util.rand_id import rand_id
from tutor.util import relational
from tutor.types.schema import (SchemaObj, Opt, sch_instance,
                                Str, Dict, Bool, Array, Type)

class Person(SchemaObj):
    '''Represents a person inside the tutor system.
    
    Person objects holds minimal information about a person that can be 
    relevant in a classroom. Person objects represents either students or
    teachers, and have information such as name, a unique id, and e-mail 
    address.
    '''
    class schema(sch_instance):
        id = Str() #@ReservedAssignment
        full_name = Str(label="Full name")
        role = Str()
        is_active = Bool(False)
        email = Opt(Str())
        comment = Str('')
        meta = Dict({})


    def __init__(self, full_name, role='student', **kwds):
        kwds.setdefault('id', rand_id('person'))
        super(Person, self).__init__(**kwds)
        self.full_name = full_name
        self.role = role

    parent = relational.ManyToOne()

class Classroom(SchemaObj):
    class schema(sch_instance):
        id = Str() #@ReservedAssignment
        course_name = Str()
        course_id = Opt(Str())
        teachers = Array(Type(Person))
        students = Array(Type(Person))
        comment = Str('')
        responses = Array()
        is_active = Bool(True)
        inbox = Opt(Type(Inbox))
        outbox = Opt(Type(Outbox))
        email_src = Opt(Type(SavingFS))

    def __init__(self, course_name, course_id=None, comment='', is_active=True):
        super(Classroom, self).__init__(course_name=course_name,
                                        course_id=course_id, comment=comment,
                                        is_active=is_active)
        self.teachers, self.students, self.responses = [], [], []
        self.id = rand_id(10)

    def __setstate__(self, obj):
        super(Classroom, self).__setstate__(obj)
        iterables = [ x for x in (self.teachers, self.students, self.responses) if x ]
        for x in itertools.chain(*iterables):
            x.parent = self

    @property
    def course(self):
        from tutor.course import globalcourse
        return globalcourse()

    #===========================================================================
    # E-mail messages
    #===========================================================================
    def mail_conf(self, email, passwd=None):
        '''Configure e-mail host for sending and receiving messages'''

        if self.outbox is not None:
            raise ValueError('already configured to %s' % self.outbox.mailfrom)

        if not email.endswith('@gmail.com'):
            raise ValueError('only Gmail e-mails are accepted...')

        if self.email_src is None:
            self.email_src = SavingFS()

        self.outbox = Outbox(self.email_src.makeopendir('outbox'), email)
        #self.inbox = Inbox(self.email_src.makeopendir('inbox'), email)

    def mail_to(self, mailto, subject='', data=None, xhtmldata=None):
        '''Creates an e-mail message to the given recipient and put it in the
        pending list'''

        if self.outbox is None:
            raise RuntimeError('outbox not configure yet')

        return self.outbox.message(mailto, subject=subject, data=data, xhtmldata=xhtmldata)

    def mail_send(self, passwd=None):
        '''Sends all pending e-mail messages'''

        if self.outbox is None:
            raise RuntimeError('outbox not configure yet')

        with self.outbox.usingpassword(passwd or self.outbox.passwd):
            self.outbox.sendmail()

    def mail_check(self, passwd=None):
        '''Checks inbox for new e-mails.'''

        if self.inbox is None:
            raise RuntimeError('inbox not configure yet')

        raise NotImplementedError

    def mail_resp(self):
        '''Prepares the e-mail feedback of all responses that were not sent
        to the students.'''

        if self.outbox is None:
            raise RuntimeError('outbox not configure yet')

        egetter = self.course.get_exam_pool
        exams = {}
        letters = 'abcdefghijklmnopqrstuvwxyz'
        id2student = {s.id: s for s in self.students}
        id2resp = {k: [] for (k, s) in id2student.items() if s.email}

        for r in (r for r in self.responses if getattr(r, 'mailpending', True)):
            s_id = r.student_id
            try:
                id2resp[s_id].append(r)
                if r.objref[0] not in exams:
                    exams[r.objref[0]] = egetter(r.objref[0])
            except:
                continue

        for st_id, student in id2student.items():
            try:
                eresplist = id2resp[st_id]
                if not eresplist:
                    continue
            except KeyError:
                continue
            line = ['Caro(a) %s,\n' % student.full_name,
                    'A correção da(s) prova(s) segue abaixo:']

            for eresp in eresplist:
                exmpool = exams[eresp.objref[0]]
                exm = exmpool[eresp.objref[1:]]
                line.append('\n  Código: %s-%s (%s)' % (tuple(eresp.objref[1:]) + (exm.title,)))
                line.append('  Nota: %0.1f' % (eresp.score * 10))
                qstvalue = 10. / len(exm)

                for i, qst in enumerate(exm):
                    qresp = eresp[qst]

                    if isinstance(qresp, Empty):
                        line.append('    %s  ) *não marcado*' % (i + 1))
                    elif isinstance(qresp, RawScore):
                        line.append('    %s  ) correção manual: %i%%' % (i + 1, 100 * qresp.score))
                    elif isinstance(qresp, ResponseSeq):
                        scoring = qst.scoring
                        for j, subq in enumerate(qst.scoring):
                            idx = '%s.%s' % (i + 1, letters[j])
                            if len(scoring) == 1:
                                idx = '%s  ' % (i + 1)
                            resp = qresp[subq]

                            if isinstance(resp, Empty):
                                line.append('    %s) *não marcado*' % idx)
                            elif isinstance(resp, RawScore):
                                line.append('    %s) correção manual: %i%%' % (idx, 100 * qresp.score))
                            else:
                                marked = ', '.join(resp.data.values())
                                correct = ', '.join(letters[subq.order.index(x)] for x in subq.correct_idx)
                                pts = subq.value / sum(sq.value for sq in qst) * qstvalue
                                line.append('    %s) marcou %s (%i%% de %0.1fpts), correto: %s' % (idx, marked, 100 * qresp.score, pts, correct))
                                if resp.score != 1:
                                    for cidx in subq.correct_idx:
                                        line.append('         Correta: %s' % subq.items[cidx].text.strip('$'))
                            if resp.data:
                                for marked in resp.data:
                                    marked = int(marked)
                                    if subq.items[marked].feedback:
                                        line.append('         Obs: %s' % subq.items[marked].feedback)

                eresp.meta['mailpending'] = False
            line.append('\nAbraço,\nFábio')
            data = '\n'.join(line)
            print student.email
            self.mail_to(student.email, subject='Correção de provas', data=str(data))

    #===========================================================================
    # Person management
    #===========================================================================
    def new_student(self, full_name, **kwds):
        '''Creates a new student'''

        self._new_person('student', full_name, **kwds)

    def new_teacher(self, full_name, **kwds):
        '''Creates a new teacher'''

        self._new_person('teacher', full_name, **kwds)

    def _new_person(self, role, full_name, **kwds):
        '''Adds a student or teacher to the classroom'''

        new = Person(full_name=full_name, role=role, **kwds)
        try:
            self._get_person(role, new.id)
        except ValueError:
            pass
        else:
            raise ValueError('a %s with the same id is already present: %s' % (role, new.id))
        new.parent = self
        getattr(self, role + 's').append(new)

    def get_student(self, id): #@ReservedAssignment
        '''Return a student with the given id'''

        return self._get_person('student', id)

    def get_teacher(self, id): #@ReservedAssignment
        '''Return a teacher with the given id'''

        return self._get_person('teacher', id)

    def _get_person(self, role, id): #@ReservedAssignment
        '''Gets a student or teacher in the classroom from the id'''
        for p in getattr(self, role + 's'):
            if p.id == id:
                return p
        else:
            raise ValueError('%s of id "%s" was not found' % (role, id))

    #===========================================================================
    # Responses management
    #===========================================================================
    def resp_add(self, resp):
        self.responses.append(resp)

    def resp_refresh(self):
        self.course.resprefresh()

    #===========================================================================
    # JSON encoding/decoding
    #===========================================================================
    def __json_encode__(self):
        json = super(Classroom, self).__json_encode__()
        json['responses'] = list(self.responses)
        json['students'] = list(self.students)
        json['teachers'] = list(self.teachers)
        if json['outbox'] is not None:
            try:
                olddir, self.outbox.dbdir = self.outbox.dbdir, None
                if self.outbox is not None:
                    json['outbox'] = pyson.json_encode(self.outbox)
                    del json['outbox']['@type']
                    del json['outbox']['fields']['dbdir']
            finally:
                self.outbox.dbdir = olddir
        return json

    @classmethod
    def __json_decode__(cls, json):
        outbox = json.pop('outbox', None)
        obj = super(Classroom, cls).__json_decode__(json)
        if outbox is not None:
            outbox['fields']['dbdir'] = obj.email_src.opendir('outbox')
            obj.outbox = Outbox.__json_decode__(outbox)
        return obj

if __name__ == '__main__':
#    from tutor.permanence import openpathjson, savepath, openpath
#    import os
#    os.chdir('../../../course_example/')
#    fname = 'turma_aa.cls'
#    cls = openpath(fname)
##    cls.mail_resp()
#    print(pyson.json_decode(pyson.json_encode(cls)))
#    cls.validate()
##    cls.mail_send('pipoca77')
##    savepath(cls, fname)
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE, verbose=0)
