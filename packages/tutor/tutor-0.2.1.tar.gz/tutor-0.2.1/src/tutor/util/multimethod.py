'''Multiple argument dispatching

Call *multimethod* on a variable number of types. It returns a decorator 
which finds the multimethod of the same name, creating it if necessary, and
adds that function to it.

For example::

    @multimethod(*types)
    def func(*args):
        pass

|

*func* is now a multimethod which will delegate to the above function, 
when called with arguments of the specified types. If an exact match can't 
be found, the next closest method is called (and cached). If there are 
multiple candidate methods, a TypeError is raised. A function can have more 
than one multimethod decorator.
        
Usage
-----

Decorate an implementation function with this class in order to create a new 
multimethod

>>> @multimethod(int, int)
... def join(x, y):
...     "Join two objects, x and y"
...     return x + y
>>> join(1, 1)
2

Other implementations can be registered using the ``@multimethod`` decorator
as long as it is used in the same module as the original multimethod

>>> @multimethod(float, float)
... def join(x, y):
...     return x + y + 0.1
>>> join(1, 1), join(1., 1.)
(2, 2.1)

The ``.dispatch()`` method of a multimethod can be used to tell explicitly
to which multimethod the evaluation should be dispatched. This way of doing 
things works across different modules/scopes.  

>>> @join.dispatch(list, list)
... def join(x, y):
...     return x + y
>>> join([1], [join(1, 1)])
[1, 2]

Multiple decorators are also accepted. The implementation function may also 
have a different name than the multimethod. In this case, the name will be 
preserved in the namespace.

>>> @join.dispatch(float, int)
... @join.dispatch(int, float)
... def join_numbers(x, y):
...     return x + y
>>> join(1, 2.), join(2., 1), join_numbers(1 + 2j, 2 + 1j)
(3.0, 3.0, (3+3j))

The multimethod is implemented as a callable dictionary that maps tuples of
types to fuctions. Another way to define an implementation is to set the 
types directly using the index notation.

>>> join[float, float] = float.__add__ 
>>> join(1., 2.)
3.0

If we don't care about one (or all of) the types, we can dispatch to the 
*anything* types. This can be done at anytime, as the multimethod always 
tries to call the most specialized implementation.

>>> @join.dispatch(anything, float)
... def join(x, y):
...     return x + y + 0.1
>>> join(1, 2.), join(1 + 0j, 2.)
(3.0, (3.1+0j))

A fallback function for any number of arguments may also be defined

>>> @join.fallback
... def join(*args):
...     return sum(args)
>>> join(1, 2, 3, 4)
10

The documentation string will be the 1st non-empty documentation string
that appear in the implementation functions

>>> join.func_doc
'Join two objects, x and y'
'''

import sys
import abc
from collections import MutableMapping

__all__ = ['multimethod', 'DispatchError', 'anything']

# *anything* type is a super type of every other type
# Workaround for different syntaxes for metaclasses in python 2.x and 3.x
@classmethod
def __subclasshook__(cls, other):
    return True
anything = abc.ABCMeta('name', (object,), {'__subclasshook__': __subclasshook__})

# Exception classes
class DispatchError(TypeError):
    pass

# Multimethod class
class multimethod(MutableMapping, dict):
    __slots__ = ['func_name', 'func_doc', 'func_dict', 'parents', 'cache', 'last']
    _slots_set_ = set(__slots__)

    #===========================================================================
    # Multimethod instance creation
    #===========================================================================
    def __new__(cls, *types):
        '''Return a decorator which will add the function to the current 
        multimethod.'''

        namespace = sys._getframe(1).f_locals

        def decorator(func):
            if isinstance(func, cls):
                self, func = func, func.last
            elif func.__name__ in namespace:
                self = namespace[func.__name__]
            else:
                self = cls.new(func.__name__)
            self[types] = self.last = func
            return self

        return decorator

    @classmethod
    def new(cls, name=''):
        '''Explicitly create a new multimethod.  
        
        Assign to local name in order to use decorator.'''

        self = dict.__new__(cls)
        self.func_name = name
        self.cache = {}
        self.parents = {None: set([None])}
        self.func_dict = {}
        self.func_doc = None
        dict.__setitem__(self, None, None)

        return self

    def dispatch(self, *types):
        '''Decorates a method from an explicit multimethod object.
        
        This can be used to spread the implementation in multiple modules or 
        using functions with different names. 
        '''

        def decorator(func):
            self[types] = self.last = func
            if self.func_name == func.__name__:
                return self
            else:
                return func

        return decorator

    def fallback(self, func):
        '''Sets the fallback function.
        
        May be called as a decorator.'''

        self[None] = func
        if func.__name__ == self.func_name:
            return self
        else:
            return func

    #===========================================================================
    # Finds parents and children
    #===========================================================================
    @staticmethod
    def is_parent(t1, t2):
        '''Return True if first argument is parent of second one.
        
        A tuple of types is parent of another tuple of types if they have the 
        same length and all types in the second are subclasses of the 
        corresponding types in the first.
        '''

        if t1 == t2:
            return False
        elif t1 is None:
            return True
        elif t2 is None:
            return False
        else:
            if len(t1) != len(t2):
                return False
            else:
                return all(map(issubclass, t2, t1))

    def get_parents(self, types):
        '''Return a set with the direct parents of a tuple of types.'''

        is_parent = self.is_parent

        # Checks which node is a direct parent to self
        parents = set()
        for node in self:
            if is_parent(node, types):
                parents.add(node)
                for p in list(parents):
                    if is_parent(node, p):
                        parents.discard(node)
                    elif is_parent(p, node):
                        parents.discard(p)

        return parents

    #===========================================================================
    # Magic methods
    #===========================================================================
    def __setitem__(self, types, func):
        self.cache.clear()
        self.parents[types] = self.get_parents(types)
        dict.__setitem__(self, types, func)

        if self.func_doc is None:
            self.func_doc = getattr(func, 'func_doc', None)

    def __getitem__(self, types):
        try:
            return dict.__getitem__(self, types)
        except KeyError as ex:
            if isinstance(types, type):
                return self[(types,)]
            else:
                raise ex

    def __delitem__(self, item):
        raise NotImplementedError

#    def __delitem__(self, types):
#        self.cache.clear()
#        dict.__delitem__(self, types)
#        for key, (value, superkeys) in self.items():
#            if types in superkeys:
#                dict.__setitem__(self, key, (value, self.parents(key)))

    def __call__(self, *args, **kwargs):
        "Resolve and dispatch to best method."

        types = tuple(type(x) for x in args)
        try:
            func = self.cache[types]
        except KeyError:
            try:
                func = self[types]
            except KeyError:
                parents = self.get_parents(types)
                if len(parents) == 1:
                    func = self[iter(parents).next()]
                else:
                    msg = ('more than one possible parent for {0}{1}: {2}'
                           .format(self.name, types, parents))
                    raise DispatchError(msg)
            self.cache[types] = func

        if func is not None:
            return func(*args, **kwargs)
        else:
            raise DispatchError('{0}{1}: no methods found'.format(self.func_name, types))

    __len__ = dict.__len__
    __contains__ = dict.__contains__
    __iter__ = dict.__iter__

    # Faster read-only dictionary methods
    (keys, items, values, get, __eq__, __ne__, __len__, __contains__, __iter__) = \
        (getattr(dict, m) for m in ['keys', 'items', 'values', 'get', '__eq__',
                                    '__ne__', '__len__', '__contains__',
                                    '__iter__'])
    def __repr__(self):
        return '<multimethod {name} at 0x{id}>'.format(name=self.name, id=id(self))

    def __getattr__(self, attr):
        try:
            return self.func_dict[attr]
        except KeyError:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        cls = type(self)
        if attr in self._slots_set_:
            getattr(cls, attr).__set__(self, value)
        else:
            self.func_dict[attr] = value

    #===========================================================================
    # Function properties
    #===========================================================================
    @property
    def func_closure(self):
        return None

    @property
    def func_code(self):
        return None

    @property
    def func_defaults(self):
        return None

    @property
    def func_globals(self):
        return sys._getframe(1).f_locals

    @property
    def __name__(self): #@ReservedAssignment
        return self.func_name

    @property
    def __doc__(self): #@ReservedAssignment
        return self.func_doc

#class ValueDispatcher(dict):
#    def __init__(self, parent=None, dispatch_after=0):
#        self.parent = parent
#        self.dispatch_after = dispatch_after
#
#    def __call__(self, *args, **kwds):
#        N = self.dispatch_after
#        typed, values = args[:N], args[N:]
#        try:
#            method = self[values]
#        except KeyError:
#            types = tuple(map(type, args))
#            raise DispatchError("{0}{1}: no methods found".format(self.parent.__name__, types))
#        else:
#            return method(*typed, **kwds)

#class vmultimethod(multimethod):
#    '''Can handle positional values as well, and dispatch according to values.
#    
#    Examples
#    --------
#    
#    Define myfunc with various signatures
#    
#    >>> @vmultimethod(int, str)
#    ... def myfunc(x, y):
#    ...     return str(x * float(y))
#    
#    >>> @vmultimethod(int, str, 'concat')
#    ... def myfunc(x, y):
#    ...     return y * x
#    
#    >>> @vmultimethod(object, object)
#    ... def myfunc(x, y):
#    ...     return 'x: %s, y: %s' % (x, y)
#    
#    
#    The computation is dispatched to each implementation automatically
#    
#    >>> myfunc(1, 2)
#    'x: 1, y: 2'
#    >>> myfunc(2, '2')
#    '4.0'
#    >>> myfunc(2, '2', 'concat')
#    '22'
#    
#    And fails if no implementation is available
#    
#    >>> myfunc(2, '2', 'foo')
#    Traceback (most recent call last):
#    ...
#    DispatchError: myfunc(<type 'int'>, <type 'str'>, <type 'str'>): no methods found
#    '''
#
#    def __setitem__(self, args, func):
#        # Separate types from values
#        types = []
#        values = []
#        for idx, arg in enumerate(args):
#            if isinstance(arg, type):
#                types.append(arg)
#            else:
#                values = tuple(args[idx:])
#                break
#        types = tuple(types)
#
#        # Set function
#        try:
#            curr_func = self[types]
#        except KeyError:
#            if values:
#                dispatcher = ValueDispatcher(self, len(types))
#                dispatcher[values] = func
#                func = dispatcher
#        else:
#            if isinstance(curr_func, ValueDispatcher):
#                curr_func[values] = func
#                func = curr_func
#            else:
#                dispatcher = ValueDispatcher(self, len(types))
#                dispatcher[()] = curr_func
#                dispatcher[values] = func
#                func = dispatcher
#
#        super(vmultimethod, self).__setitem__(types, func)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
