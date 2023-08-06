#-*- coding: utf8 -*-
from pyson.schemas import (Schema, Str, Bool, Array, Lang)
from tutor.config import settings

__all__ = 'Student Course Classroom'.split()

Student = Schema({ u'school_id': Str(is_ref=True),
                   u'full_name': Str(label='Nome completo do estudante'),
                   u'email?': Str(),
                   u'is_active?': Bool(True),
                   u'comment?': Str() },
                 name='Student')

Course = Schema({ u'course_id': Str(is_ref=True),
                  u'title': Str(),
#                  u'lang?': Lang(settings.DEFAULT_LANGUAGE),
                  u'is_active?': Bool(True),
                  u'comment?': Str()},
                name='Course')

Classroom = Schema({ u'course': Str(),
                     u'classroom_id': Str(),
                     u'teacher': Str(),
                     u'students': Array(Str),
                     u'is_active?': Bool(True),
                     u'comment?': Str() },
                   name='Classroom')
