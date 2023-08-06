#-*- coding: utf-8 -*-
from tutor.db.base import ORMModel
from tutor.config import schemas
__all__ = [ 'Student', 'Course' ]

class Student(ORMModel):
    """Represents a student.
    
    Example
    -------

    # May initialize using the 'from_keys' method
    >>> std = Student.from_keys(full_name='Douglas Adams', school_id='42')
    >>> std.pprint()
    [ Student '42' ]
        full_name: Douglas Adams
    
    # Object can be build from json structure
    >>> std = Student.from_json({'full_name': 'Douglas Adams', 'school_id': '42'})
    >>> std.pprint()
    [ Student '42' ]
        full_name: Douglas Adams
        
    # Object can be loaded from lib as a single object or as a list of objects
    >>> std = Student.from_lib('examples/id42')
    >>> std.full_name
    u'Arthur Dent'
    
    >>> std_list = Student.from_lib('examples/class')
    >>> [ std.full_name for std in std_list ]
    ['Arthur Dent', 'Douglas Adams']
    """

    schema = schemas.Student
    db_fields = ['school_id', 'full_name', 'is_active']


class Course(ORMModel):
    """Represents a course
    
    Example
    -------
    
    >>> c = Course.from_keys('c3', 'Calculo 3')
    >>> c.pprint()
    [ Course 'c3' ]
        title: Calculo 3
        lang: pt-br
    """

    schema = schemas.Course
    db_fields = ['course_id', 'title', 'is_active']

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
