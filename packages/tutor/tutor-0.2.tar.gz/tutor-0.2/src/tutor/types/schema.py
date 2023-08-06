from __future__ import absolute_import, print_function, unicode_literals, division
if __name__ == '__main__':
    __package__ = b'tutor.types' #@ReservedAssignment
    import tutor.types #@UnusedImport

import copy
import functools
from datetime import date as _date, datetime as _datetime
from fs.base import FS as _FS
from pyson.json_encoding import register_cls
from pyson.pyson_collections import MapView
from pyson.schema import * #@UnusedWildImport

#===============================================================================
# Schema Object
#===============================================================================
class SchemaObj(object):
    '''SchemaObj subclasses implement the interface defined by a pyson Object 
    schema. 
    
    Keys in dictionary are interpreted as attributes. The ``.dictview`` 
    attribute returns a view of the object with a dictionary-like interface. 
    '''

    class __metaclass__(type):
        def __new__(cls, name, bases, namespace):
            try:
                schema = namespace.get('schema', None) or bases[0].schema

            # Class does not have a schema attribute defined
            except AttributeError:
                if bases[0] is not object:
                    def __getattr__(self, attr):
                        try:
                            return self._data[attr]
                        except KeyError:
                            raise AttributeError(attr)

                    def __setattr__(self, attr, value):
                        try:
                            self._data[attr] = value
                        except KeyError:
                            raise AttributeError(attr)

                    namespace.setdefault('__getattr__', __getattr__)
                    namespace.setdefault('__setattr__', __setattr__)

            # Class has a schema: limit attributes and create descriptors for
            # each schema key
            else:
                schema.label = schema.label if schema.label != 'schema' else name
                namespace['_keys'] = set(schema.keys())
                for key, sch in schema.items():
                    key = str(key)
                    fget = functools.partial(cls.fget, key, sch)
                    fset = functools.partial(cls.fset, key, sch)
                    namespace[key if key not in namespace else '_' + key] = property(fget, fset)

            if len(bases) == 1:
                namespace.setdefault('__slots__', ('_data', '_cache', '_dictview'))
            json_name = namespace.pop('json_name', name)
            new = type.__new__(cls, name, bases, namespace)

            # Viewer class: can be specialized, if a schema is defined,
            try:
                keys = schema.keys()
            except NameError:
                new._viewtype = MapView
            else:
                new._viewtype = MapView.subclass(new, keys)


            # JSON register
            if json_name != 'SchemaObj':
                json_name = (json_name if json_name.startswith('tutor.')
                                       else 'tutor.' + json_name)
                register_cls(json_name)(new)
            return new

        @staticmethod
        def fget(key, sch, self):
            try:
                return self._data[key]
            except KeyError:
                try:
                    return sch.default_or_null
                except AttributeError:
                    raise AttributeError("'%s' attribute of '%s' object is empty" % (key, type(self).__name__))

        @staticmethod
        def fset(key, sch, self, value):
            if value != sch.default_or_null:
                self._data[key] = value

    # Object creation and initialization ---------------------------------------
    def __init__(self, **kwds):
        self.__setstate__(kwds)

    @classmethod
    def from_data(cls, data, copy=True):
        '''Creates a new instance from a data dictionary.'''

        if copy:
            data = dict(data)
        new = SchemaObj.__new__(cls)
        new.__setstate__(data)
        return new

    @property
    def dictview(self):
        return self._dictview

    # Validation/adaptation ----------------------------------------------------
    def validate(self, **kwds):
        '''Validate data in object'''

        self.schema.validate(self._data, **kwds)

    def isvalid(self, **kwds):
        '''Validate data in object'''

        self.schema.isvalid(self.dictview)

    def adapt(self, inplace=False, **kwds):
        '''Adapt data in object to a valid state.'''

        if inplace == False:
            new = self.copy()
            return new.adapt(inplace=True, **kwds)

        self.schema.adapt(self.dictview, inplace=True, **kwds)
        return self

    def copy(self):
        '''Creates a copy of itself'''

        return self.from_data(copy.deepcopy(self._data))

    # JSON encoding ------------------------------------------------------------
    def __json_encode__(self):
        return dict(self.dictview)

    @classmethod
    def __json_decode__(cls, json):
        return cls.from_data(json)

    # Pickling and copying -----------------------------------------------------
    def __getstate__(self):
        return self._data

    def __setstate__(self, state):
        object.__setattr__(self, '_dictview', self._viewtype(self))
        object.__setattr__(self, '_cache', {})

        schema = self.schema
        bad_kwds = set(state) - set(schema)
        if not bad_kwds:
            for k, v in state.items():
                if v == schema[k].default_or_null:
                    del state[k]
            object.__setattr__(self, '_data', state)
        else:
            raise TypeError('invalid argument in constructor of %s object: %s' % (type(self).__name__, bad_kwds.pop()))

        for k, v in state.items():
            if k in self._keys:
                setattr(self, k, v)
            else:
                raise ValueError('invalid keyword argument: %s' % k)

        if hasattr(self, 'init'):
            raise RuntimeError('init is deprecaded')

#===============================================================================
# Create special type schemas
#===============================================================================
Date = type_schema_factory(_date)
Datetime = type_schema_factory(_datetime)

# Mappings
Dict = type_schema_factory(dict)

# Folder
Folder = type_schema_factory(_FS)

