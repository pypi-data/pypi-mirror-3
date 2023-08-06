#-*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from future_builtins import *
import tutor.config
from tutor.db.base import models
from tutor.db.person import Person
from tutor.db.course import Course

#===============================================================================
#                                Classroom
#===============================================================================
class Classroom(models.ORMModel, models.Printable):
    """Represents a classroom.
    
    
    Example
    -------
    
    # Create a teacher and course
    >>> einstein = Person.from_keys('Albert Einstein', 'id123',)
    >>> gen_rel = Course.from_keys('General Relativity', 'ex123')
    
    # Create new classroom
    >>> c = Classroom.from_keys('A', gen_rel, einstein)
    
    # Add students to classroom
    >>> c.add_students(Person.from_lib('example', role='student'))
    >>> c.pprint()
    [ Classroom "General Relativity - A"]
        teacher: Albert Einstein
        STUDENTS
          * Douglas Adams (id1)
          * Arthur Dent (id2)
    """

    schema = tutor.config.schemas.Classroom
    classroom_id = models.CharField(max_length=5)
    course = models.ForeignKey(Course)
    teacher = models.ForeignKey(Person, related_name='classroom_as_teacher')
    is_active = models.BooleanField(default=False)
    _students = models.ManyToManyField(Person, related_name='classroom_as_student')

    class Meta:
        unique_together = (('classroom_id', 'course'))

    @staticmethod
    def from_keys(classroom_id, course, teacher, **kwds):
        cls, _ = Classroom.objects.get_or_create(course=course,
                                                 classroom_id=classroom_id,
                                                 teacher=teacher)
        cls.check_keys(kwds)
        for k, v in kwds.items():
            setattr(cls, k, v)
        cls.save()
        return cls

    def json_backup(self):
        '''
        
        '''
        pass

    def json_load(self, json):
        pass

    def add_student(self, student):
        '''
        Add 'student' to Classroom
        '''

        # Check if Person is an student
        if student.role != 'student':
            role = student.role
            role = role if role is not None else 'unknown role'
            raise TypeError('must be a student, got ' + repr(role))

        # Add student
        self._students.add(student)

    def add_students(self, student_list):
        '''
        Add all students in student_list to Classroom
        
        
        Arguments
        ---------
        
        student_list : list of Person objects
            List of students.
        '''
        for student in student_list:
            self.add_student(student)

    # Properties ---------------------------------------------------------------
    @property
    def student_ids(self):
        return list(self._students.values_list('school_id', flat=True))

    @property
    def students(self):
        return list(self._students.all())

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
