from __future__ import absolute_import

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from binpack import BinPack, JSON, Compressed, String, header
from pyson.schema import ValidationError
import pyson

class AddDict(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise KeyError('key already exists: %s' % key)
        else:
            super(AddDict, self).__setitem__(key, value)

class BadHeaderError(ValueError):
    pass

#===============================================================================
# Tutor objects permanence
#===============================================================================
HasIdFile = BinPack.new_type('HasIdFile', 'TUTOR::OBJECT', '0.1')
HasIdFile.add_field('id')
HasIdFile.lock()

TutorFile = None
class TutorFile(HasIdFile):
    DUMP_FUNCS = AddDict()
    LOAD_FUNCS = AddDict()
    LOADJSON_FUNCS = AddDict()

    class __metaclass__(type(HasIdFile)):
        binpack_cls = type(BinPack)

        def __new__(cls, name, bases, namespace):
            if TutorFile is None:
                return type.__new__(cls, name, bases, namespace)

            # Set defaut values for class constants
            type_ = namespace['obj_type']
            tname = type_.__name__

            # Creates type
            new = cls.binpack_cls.__new__(cls, name, bases, namespace)
            new.set_header(namespace.get('header', 'TUTOR::%s' % tname.upper()))
            new.set_version(namespace.get('version', '0.1'))

            # Register load and dump functions
            new.LOAD_FUNCS[new.get_header()] = new.load
            new.LOADJSON_FUNCS[new.get_header()] = new.loadjson
            new.DUMP_FUNCS[type_] = new.dump

            return new

    @classmethod
    def loadjson(cls, F):
        '''Loads object from file object'''

        # Load JSON
        json = {}
        with cls(F) as data:
            fields = list(cls.get_fields())
            for f in fields[:-1]:
                json[f] = data[f]
            json.update(data[fields[-1]])

        return json


    @classmethod
    def load(cls, F, conv=False):
        '''Loads object from file object'''

        json = cls.loadjson(F)
        try:
            result = pyson.json_decode(json)
        except Exception as ex:
            if conv:
                from . import robust
                result = robust.BadJSON(json, ex)
            else:
                raise

        # Is it the right type?
        if not isinstance(result, cls.obj_type):
            raise TypeError('unexpected output for load(): expected %s object, but got %s object' % (cls.obj_type, type(result)))

        return result

    @classmethod
    def loads(cls, st, conv=False):
        '''Loads object from string'''

        return cls.load(StringIO(st), conv)

    @classmethod
    def dump(cls, obj, F, atomic=True, force=False):
        '''Saves object in file object'''

        try:
            obj.validate()
        except ValidationError:
            if force:
                obj = obj.adapt()
            else:
                raise

        json = pyson.json_encode(obj)
        with cls(F, 'w', atomic=atomic) as data:
            fields = list(cls.get_fields())
            for f in fields[:-1]:
                data[f] = json.pop(f)
            data[fields[-1]] = json

    @classmethod
    def dumps(cls, obj, force=False):
        '''Saves object to string'''

        F = StringIO()
        cls.dump(obj, F, atomic=False, force=False)
        return F.getvalue()

#===============================================================================
# dump, load, dumps, loads functions
#===============================================================================
def dump(obj, F, atomic=True, force=False):
    dump = TutorFile.DUMP_FUNCS
    try:
        dumpfunc = dump[type(obj)]
    except KeyError:
        raise TypeError('object of type %s is not supported' % type(obj))
    else:
        return dumpfunc(obj, F, atomic, force)

def load(F, conv=False):
    header_data = header(F)
    try:
        loader = TutorFile.LOAD_FUNCS[header_data]
    except KeyError:
        msg = 'unrecognized header: %s' % header_data
        if conv:
            from . import robust
            return robust.BadHeaderLoad(F.read(), BadHeaderError(msg))
        else:
            raise BadHeaderError(msg)

    return loader(F, conv)

def dumps(obj, force=False):
    '''Serializes object to string'''

    F = StringIO()
    dump(obj, F, atomic=False, force=force)
    return F.getvalue()

def loads(st, conv=False):
    '''Loads object from string'''

    return load(StringIO(st), conv)

def openpath(path, conv=False):
    '''Returns object saved in file in the given path'''

    with open(path) as F:
        return load(F, conv)

def savepath(obj, path, force=False):
    '''Saves object in the given path'''

    data = dumps(obj, force)
    with open(path, 'w') as F:
        F.write(data)

def loadjson(F):
    header_data = header(F)
    try:
        loader = TutorFile.LOADJSON_FUNCS[header_data]
    except KeyError:
        msg = 'unrecognized header: %s' % header_data
        raise BadHeaderError(msg)

    return loader(F)

def loadsjson(st):
    return loadjson(StringIO(st))

def openpathjson(path):
    with open(path) as F:
        return loadjson(F)

#===============================================================================
# QuestionPool
#===============================================================================
from tutor.types import QuestionPool
class QuestionFile(TutorFile):
    version = '0.1'
    header = 'TUTOR::QUESTION'
    obj_type = QuestionPool

QuestionFile.add_field('name', String())
QuestionFile.add_field('title', String(u''))
QuestionFile.add_field('author', String(u''))
QuestionFile.add_field('version', String())
QuestionFile.add_field('data', Compressed(JSON(use_decimal=True), 'bz2'))
QuestionFile.lock()

#===============================================================================
# ExamPool
#===============================================================================
from tutor.types import ExamPool
class ExamFile(TutorFile):
    version = '0.1'
    header = 'TUTOR::EXAM'
    obj_type = ExamPool

ExamFile.add_field('name', String())
ExamFile.add_field('title', String(u''))
ExamFile.add_field('author', String(u''))
ExamFile.add_field('version', String())
ExamFile.add_field('data', Compressed(JSON(use_decimal=True), 'bz2'))
ExamFile.lock()

#===============================================================================
# Students
#===============================================================================
from tutor.types import Classroom
class ClassroomFile(TutorFile):
    version = '0.1'
    header = 'TUTOR::CLASSROOM'
    obj_type = Classroom

ClassroomFile.add_field('course_name', String())
ClassroomFile.add_field('course_id', String())
ClassroomFile.add_field('data', Compressed(JSON(use_decimal=True), 'bz2'))
ClassroomFile.lock()

#===============================================================================
# Students
#===============================================================================
from tutor.types import ResponsePool
class ResponseFile(TutorFile):
    version = '0.1'
    header = 'TUTOR::RESPONSE'
    obj_type = ResponsePool

ResponseFile.add_field('pool_id', String())
ResponseFile.add_field('pool_rev', String())
ResponseFile.add_field('data', Compressed(JSON(use_decimal=True), 'bz2'))
ResponseFile.lock()

if __name__ == '__main__':
    o = Classroom('physics')
    print pyson.json_encode(o)
    print loads(dumps(o)).course_name

