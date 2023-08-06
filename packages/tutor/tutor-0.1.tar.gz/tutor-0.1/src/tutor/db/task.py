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
from tutor.db.activity import Activity

#===============================================================================
#                                Task
#===============================================================================
class Task(models.ORMModel, models.Printable):
    """Creates a task.    """

    schema = tutor.config.schemas.Task
    student = models.ForeignKey(Person)
    _activity = models.ForeignKey(Activity)
    exam = models.ForeignKey(Exam)
    _ctime = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    @staticmethod
    def from_keys(student, activity, exam, **kwds):
        t = Task(student=student, _activity=activity, exam=exam)
        t.check_keys(kwds)
        for k, v in kwds.items():
            setattr(t, k, v)
        t.save()
        return t

    # API ----------------------------------------------------------------------

    # Properties ---------------------------------------------------------------

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
    def activity(self):
        return self._activity

    @property
    def activity_id(self):
        A = self._activity
        return (A.classroom.course_id, A.classroom_id)

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)

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
    task = tasks[0]
    task.pprint()
    print(task.exam.latex().encode('utf8'))

