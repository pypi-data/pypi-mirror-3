#-*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from future_builtins import *
from datetime import datetime
import tutor.config
from tutor.db.base import models
from tutor.db.course import Course
from tutor.db.person import Person
from tutor.db.classroom import Classroom
from tutor.db.exam import Exam

#===============================================================================
#                                Activity
#===============================================================================
class Activity(models.ORMModel, models.Printable):
    """Represents an activity.
    
    
    Usage
    -----
    
    # Create teacher, course, and exam
    >>> einstein = Person.from_keys('Albert Einstein', 'id123',)
    >>> gen_rel = Course.from_keys('General Relativity', 'ex123')
    >>> exam = Exam.from_lib('examples/simple_exam')

    # New classroom
    >>> cls = Classroom.from_keys('A', gen_rel, einstein)

    # Add students to classroom
    >>> cls.add_students(Person.from_lib('example', role='student'))
    >>> actv = Activity.from_keys(cls, exam)
    >>> actv.pprint() #doctest: +ELLIPSIS
    [ Activity in course General Relativity - A]
        exam: Simple Exam
        creation time: ...
        grade: 1
    """

    schema = tutor.config.schemas.Activity
    _classroom = models.ForeignKey(Classroom)
    exam = models.ForeignKey(Exam)
    _ctime = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    @staticmethod
    def from_keys(classroom, exam, **kwds):
        class_id = classroom.classroom_id
        course_id = classroom.course_id

#        # Compute name
#        name = '{0}-{1}::{2}::'.format(course_id, class_id, exam.name)
#        query = Activity.objects.filter(name__startswith=name)
#        query = query.values_list('name', flat=True)
#        ids = set(int(pk[len(name):]) for pk in query)
#        for idx in range(len(ids) + 1):
#            if idx not in ids:
#                name = name + str(idx)
#                break

        a = Activity(_classroom=classroom, exam=exam)
        a.check_keys(kwds)
        for k, v in kwds.items():
            setattr(a, k, v)
        a.save()
        return a

    # API ----------------------------------------------------------------------
    def create_tasks(self):
        '''
        Create all student tasks.
        '''
        from tutor.db.task import Task

        tasks = []
        for student in self.classroom.students:
            exam = self.exam.new_child()
            exam.student_name = student.full_name
            exam.student_id = student.school_id
            exam.teacher = self.classroom.teacher.full_name
            exam.save()
            task = Task.from_keys(student, self, exam)
            tasks.append(task)
        return tasks

    # Properties ---------------------------------------------------------------
    @property
    def tasks(self):
        return list(self.task_set.order_by('student__full_name'))

    @property
    def has_tasks(self):
        pass

    @property
    def course_id(self):
        return self._classroom.course_id

    @property
    def classroom_id(self):
        return self._classroom.classroom_id

    @property
    def course(self):
        return self._classroom.course

    @property
    def classroom(self):
        return self._classroom

    # ctime attribute.
    def _ctime_get(self):
        dt = self._ctime
        keys = [u'day', u'month', u'year', u'hour', u'minute', u'second', u'microsecond']
        return dict((k, getattr(dt, k)) for k in keys)
    def _ctime_set(self, v):
        self._ctime = datetime(**v)
    ctime = property(_ctime_get, _ctime_set)

    @property
    def ctime_obj(self):
        return self._ctime

    @property
    def title(self):
        return self.exam.title

if __name__ == '__main__':
#    import doctest
#    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)

    # Create teacher, course, and exam
    einstein = Person.from_keys('Albert Einstein', 'id123',)
    gen_rel = Course.from_keys('General Relativity', 'ex123')
    exam = Exam.from_lib('examples/simple_exam')

    # New classroom
    cls = Classroom.from_keys('A', gen_rel, einstein)

    # Add students to classroom
    cls.add_students(Person.from_lib('example', role='student'))
    actv = Activity.from_keys(cls, exam)
    tasks = actv.create_tasks()
    actv.pprint()
    actv.exam.pprint()
    print(actv.latex_document())
