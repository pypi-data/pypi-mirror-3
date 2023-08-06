#-*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
from future_builtins import *
import sys
import itertools
import time
import hashlib
import json
from cStringIO import StringIO
from tutor.config import schemas
from tutor.filters import default_filters
from tutor.util import jsonlib
from tutor.db.base import ORMModel, HasChildren
from tutor.db.nodes import *
from tutor.lib.loaders import learning_obj as loaders

__all__ = [ 'LearningObj' ]

#===============================================================================
#                                LEARNING OBJECT
#===============================================================================
class LearningObj(ORMModel, HasChildren):
    """
    LearningObj objects represents a task to the student. It can be a question 
    from a test, an interactive tutorial, some explanation, etc. Learning 
    objects can be latter organized into Exams and similar tasks.
    
    LearningObj templates are stored in the tutor_lib directory (by default it 
    is /usr/lib/tutor). Each template address may correspond to one (or more) 
    files in this directory. These templates are loaded as a LearningObj and 
    can be used to create other derived LearningObj's on request. Many templates
    are parametrized with Python code that generates several similar, but not 
    identical versions.
    
    Example
    -------
    
    # Reset database
    >>> addr = 'examples/lyx_simple'
    >>> LearningObj.objects.filter(template_name=addr).delete()
    
    # Loads objects from an empty database
    >>> lt = LearningObj.from_lib(addr)
    >>> lo_0 = lt.child()
    >>> lo_1 = lt.child()
    >>> lo_0.template_name == lt.template_name
    True
    
    # Names are created automatically from addr
    >>> print(lt.name)
    examples/lyx_simple
    >>> print(lo_0.name)
    examples/lyx_simple::0
    >>> print(lo_1.name)
    examples/lyx_simple::1
    
    # Items are shuffled when a new object is created
    >>> assert not (lt.content[0].items == lo_0.content[0].items 
    ...             == lo_1.content[0].items)
    
    # Can output latex
    >>> latex = lt.latex()
    >>> 'Ultimate Question of Life, the Universe, and Everything' in latex
    True
    
    >>> lo = LearningObj.from_template('examples/lyx_simple')
    
    # Names
    >>> print(lo.name) # doctest: +ELLIPSIS
    examples/lyx_simple::...
    >>> print(lo.template_name)
    examples/lyx_simple
    
    # The children is different from parent
    >>> lo.template.content[0].items != lo.content[0].items
    True
    """

    schema = schemas.LearningObj
    db_fields = ['name', 'template_name', 'is_template', 'parent', 'title', 'is_active']
    db_fields_init = { 'parent': { 'null': True } }

    def child(self, **kwds):
        kwds['_save'] = False
        ntries = kwds.setdefault('_ntries', 10)
        child = super(LearningObj, self).child(**kwds)

        # Apply namespace rule, if namespace exists
        if child.namespace_pool:
            names = Pool(child._json['namespace_pool'], self)()
            subs = {}
            for sub in child.namespace_subs:
                vars = ([n['var_name']] + n['filters'] for n in sub['substitutions'])
                subs[sub['path']] = (sub['text'], tuple(vars))
            subs = jsonlib.compute_subs(subs, names, default_filters)
            jsonlib.jpath_update(child._json, subs)

        if 'namespace_pool' in child._json:
            del child._json['namespace_pool']

        if 'namespace_subs' in child._json:
            del child._json['namespace_subs']

        # Check for repeated fields and randomize content
        for node in child.content:
            assert_unique = getattr(node, 'assert_unique_items', lambda: None)
            try:
                assert_unique()
            except ValueError as ex:
                if ntries > 0:
                    kwds['_ntries'] -= 1
                    return self.child(**kwds)
                else:
                    raise ex
            node.refresh()

        # Return saved object
        child.pre_save()
        child.save()
        return child

    def pre_save(self):
        '''
        Update hash according to JSON data before saving new object.
        '''

        json_obj = self.json(raw=True)
        json_str = json.dumps(json_obj)
        hash = hashlib.md5(json_str).hexdigest()
        hash = hash if len(hash) < 50 else hash[:50]
        self.hash = hash

    def pretty(self, **kwds):
        #TODO: should output datetime objects as default
        import datetime
        date = datetime.date(**self.date)
        kwds.setdefault('date', date)
        return super(LearningObj, self).pretty(**kwds)

    # JSON properties ----------------------------------------------------------
    def T_content_json(self, obj):
        return [ item.json_raw for item in obj ]

    def T_content_object(self, json):
        return [ Node(item, self) for item in json ]

    def T_namespace_pool_json(self, obj):
        return obj.json_raw

    def T_namespace_pool_object(self, json):
        return Pool(json, parent=self)

    def __unicode__(self):
        return "<LearningObj '%s'>" % self.name

    __str__ = __repr__ = __unicode__

#===============================================================================
#                             NAMESPACE POOLS
#===============================================================================
class Pool(object):
    types = {}
    def __new__(cls, json=None, parent=None, **kwds):
        if cls is Pool:
            if json is None:
                return None
            try:
                return Pool.types[json['type']](json, parent, **kwds)
            except KeyError:
                return object.__new__(Pool)
        else:
            return object.__new__(cls)

    def __init__(self, json=None, parent=None, **kwds):
        if json is None:
            json = {}
        json.update(kwds)
        self._json = json
        self.parent = parent
        if parent is None:
            raise

    def __call__(self):
        raise RuntimeError('must be overridden by children class')

    def __nonzero__(self):
        return bool(self._json)

@jsonlib.json_properties(schemas.LearningObj['namespace_pool'])
class PythonNS(Pool):
    extension = '.py'
    def __call__(self, ntries=10):
        stdold = sys.stderr, sys.stdout
        stdtmp = StringIO()
        try:
            sys.stderr = sys.stdout = stdtmp
            namespace_dic = {}
            code = self.code.strip()
            if code.startswith('#-*-'):
                code = '\n'.join(code.splitlines()[1:])
            try:
                exec code in namespace_dic
            except Exception as ex:
                msg = 'Exception caught executing %s\n' % self.parent.name
                stdold[1].write(msg)
                stdold[1].write(stdtmp.getvalue())
                raise ex
        except AssertionError as ex:
            if ntries > 0:
                return self(ntries - 1)
            else:
                raise ex
        finally:
            sys.stderr, sys.stdout = stdold

        return dict((name, namespace_dic.get(name, '')) for name in self._json['names'])

Pool.types['python'] = PythonNS

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
