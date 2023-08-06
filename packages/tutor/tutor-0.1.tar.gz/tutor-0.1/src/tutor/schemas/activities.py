#-*- coding: utf8 -*-
from tutor.util.jsonlib import (Schema, Str, Bool, Ref, Number, Array, 
                                JSONDateTime)

__all__ = 'Exam Activity Task'.split()

Exam = Schema({ u'name': Str(is_ref=True),
                u'is_template': Bool(False),
                u'template_name?': Str(),
                u'parent': Ref('self'),
                u'title': Str(),
                u'type?': Str(),
                u'subtitle?': Str(),
                u'author?': Str(),
                u'content?': Array(Str(), name='Content'),
                u'lang?': Str(),
                u'version?': Str(),
                u'is_active': Bool(True),
                u'comment?': Str() },
              name='Exam')

Activity = Schema({ u'course_id': Str(),
                    u'classroom_id': Str(),
                    u'exam_id': Str(),
                    u'ctime': JSONDateTime(),
                    u'grade': Number(1),
                    u'is_active': Bool(True),
                    u'comment': Str() },
                  name='Activity')

Task = Schema({ u'exam_id': Str(),
                u'activity_id': Array(Str),
                u'student_id': Str(),
                u'is_active': Bool(True),
                u'ctime': JSONDateTime(),
                u'responses': Array(),
                u'grade?': Number(),
                u'comment': Str() },
              name='Task')
