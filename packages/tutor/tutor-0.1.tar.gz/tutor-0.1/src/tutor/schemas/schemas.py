#-*- coding: utf8 -*-
from tutor.util.jsonlib.all import (Schema, Str, Int, Bool, Number, Array,
    JSONDateTime, JSONDate, Anything, Lang)
DEFAULT_LANGUAGE = 'en' #TODO: extract from settings

__all__ = [ 'MultipleChoiceItem', 'MultipleChoice', 'TrueFalseItem', 'TrueFalse',
            'Association', 'AssociationItem', 'Text', 'Node', 'Citation',
            'LearningObj', 'Exam', 'Activity', 'Course' ]

#TODO: move this to JSONlib and support proper subclassing
class SchemaClass(object):
    class __metaclass__(type):
        def __new__(cls, name, bases, dict):
            if name == 'SchemaClass':
                return type.__new__(cls, name, bases, dict)
            else:
                del dict['__module__']
                return Schema(dict, name=name)

#===============================================================================
#                 Validators for atomic question types: 
#                e.g., multiple choice, true/false, association, etc
#===============================================================================
QUESTION_NODES = ['multiple-choice', 'true-false', 'association']
DISPLAY_NODES = ['text']

# Multiple Choice --------------------------------------------------------------
schema = {
    u'value': Number(0.0),
    u'text': Str(),
    u'id': Int(),
    u'feedback?': Str(),
    u'comment?': Str(),
}
MultipleChoiceItem = Schema(schema, name='MultipleChoiceItem')

MultipleChoice = Schema({ u'type': 'multiple-choice',
                          u'stem': Str(),
                          u'value': Number(1.0),
                          u'shuffle?': Bool(True),
                          u'multiple_answers?': Bool(False),
                          u'name?': Str(),
                          u'response?': Int() | Array(Int()),
                          u'score?': Number(0.0),
                          u'columns?': Int(),
                          u'items': Array(MultipleChoiceItem, name='Items'),
                          u'solution?': Str(),
                          u'comment?': Str() },
                        name='MultipleChoice')

# True/False -------------------------------------------------------------------
schema = {
    u'answer': Bool(),
    u'response?': Bool(),
    u'value': Number(1.0),
    u'text': Str(),
    u'text_other?': Str(),
    u'feedback?': Str(),
    u'comment?': Str(),
}
TrueFalseItem = Schema(schema, name='TrueFalseItem')

schema = {
    u'type': 'true-false',
    u'stem': Str(),
    u'shuffle?': Bool(True),
    u'items': Array(TrueFalseItem, name='Items'),
    u'value': Number(1.0),
    u'comment?': Str(),
}
TrueFalse = Schema(schema, name='TrueFalse')

# Association ------------------------------------------------------------------
schema = {
    u'text_image': Str(),
    u'text_domain': Str(),
    u'feedback?': Str(),
    u'comment?': Str(),
    u'value': Number(1.0),
}
AssociationItem = Schema(schema, name='AssociationItem')

schema = {
    u'type': 'association',
    u'stem': Str(),
    u'shuffle?': Bool(True),
    u'items?': Array(AssociationItem, name='Items'),
    u'image_ordering?': Array(Int),
    u'columns_domain?': Int(),
    u'columns_image?': Int(),
    u'columns?': Int(),
    u'comment?': Str(),
    u'value': Number(1.0),
}
Association = Schema(schema, name='Association')

# Mapping ----------------------------------------------------------------------
class MappingImageItem(SchemaClass):
    id = Int()
    text = Str()
    comment = Str(is_optional=True)

class MappingDomainItem(SchemaClass):
    id = Int()
    text = Str()
    feedback = Str(is_optional=True)
    comment = Str(is_optional=True)
    value = Number(1.0)

class Mapping(SchemaClass):
    type = u'mapping'
    stem = Str()
    shuffle = Bool(True, is_optional=True)
    domain = Array(MappingDomainItem, name='domain')
    image = Array(MappingImageItem, name='image')
    mapping = Anything() # TODO: dictionary schema

# Text Nodes -------------------------------------------------------------------
schema = {
    u'type': 'text',
    u'text': Str(),
}
Text = Schema(schema, name='Text')

# Nodes ------------------------------------------------------------------------
Node = Text | TrueFalse | MultipleChoice | Association
NODES = { 'text': Text, 'true-false': TrueFalse,
          'multiple-choice': MultipleChoice, 'association': Association }

#===============================================================================
#                                    LearningObj
#===============================================================================
Citation = Schema({ u'type': Str(),
                    u'full_ref': Str(),
                    u'cite': Str() },
                  name='Citation')

LearningObj = Schema({
    # Database info and behavior
    u'name': Str(is_ref=True),
    u'is_template': Bool(False),
    u'template_name?': Str(),
    u'type?': Str(),
    u'lang?': Str(),
    u'creation_time?': JSONDateTime(),
    u'version?': Str(),
    u'hash?': Str(),
    u'is_active?': Bool(True),
    u'comment?': Str(),

    # Scoring
    u'value?': Number(1.0),
    u'score?': Number(0),

    # Meta information
    u'title': Str(),
    u'author': Str(),
    u'date': JSONDate(),
    u'difficulty?': Int(),

    # Content
    u'content': Array(Node()),
    u'glossary?': Array(Array(Str())),
    u'bibliography?': Array(Citation()),
    u'further_reading?': Array(Citation()),

    # Namespace
    u'namespace_pool?': Schema({ u'type': Str(),
                                 u'code': Str(),
                                 u'var_names': Array(Str())}),
    u'namespace_subs?': Anything(), # Change to Dictionary 

    # Feedback to students
    u'solution?': Str(),
    u'grade_feedback?': Schema({
        u'maximum': Str(),
        u'null': Str(),
        u'intermediate': Str(),
    }),
}, name='LearningObj')

#===============================================================================
#                            Exams and tasks
#===============================================================================
Exam = Schema({ u'name': Str(is_ref=True),
                u'is_template': Bool(False),
                u'template_name?': Str(),
                u'creation_time?': JSONDateTime(),
#                u'parent?': Ref('self'),
                u'title': Str(),
                u'type?': Str(),
                u'subtitle?': Str(),
                u'author?': Str(),
                u'content?': Array(Str(), name='Content') | Anything(), # Learning Obj
                u'lang?': Str(),
                u'version?': Str(),
                u'is_active': Bool(True),
                u'comment?': Str(),
                u'value?': Number(1.0),
                u'score?': Number(0) },
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

#===============================================================================
#                             Site objects
#===============================================================================
Student = Schema({ u'school_id': Str(is_ref=True),
                   u'full_name': Str(label='Nome completo do estudante'),
                   u'email?': Str(),
                   u'is_active?': Bool(True),
                   u'comment?': Str() },
                 name='Student')

Course = Schema({ u'course_id': Str(is_ref=True),
                  u'title': Str(),
                  u'lang?': Lang(DEFAULT_LANGUAGE),
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

for var in dir():
    if var.isupper():
        __all__.append(var)
