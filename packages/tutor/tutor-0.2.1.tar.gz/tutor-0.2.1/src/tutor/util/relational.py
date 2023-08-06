import collections

class relset(collections.MutableSet):
    def __init__(self, destination, sources, value):
        self._values = {}
        self.destination = destination
        self.sources = sources
        self.value = value

    def __iter__(self):
        return self._values.itervalues()

    def __contains__(self, obj):
        return id(obj) in self._values

    def add(self, obj):
        id_obj = id(obj)
        self._values[id_obj] = obj
        if id_obj in self.destination:
            self.sources[id(self.destination[id_obj])].discard(id_obj)
        self.destination[id_obj] = self.value

    def discard(self, obj):
        id_obj = id(obj)
        self._values.pop(id_obj, None)
        self.destination.pop(id_obj, None)

    def __repr__(self):
        return 'set([%s])' % (', '.join(repr(x) for x in self))

    def __len__(self):
        return len(self._values)

class Relation(object):
    '''Relation classes are descriptors that implement the traditional 
    one-to-one, one-to-many and many-to-many relations found in any relational
    database.
    
    >>> class Foo(object):
    ...     def __init__(self, value): self.value = value
    ...     def __repr__(self): return self.value
    ... 
    ...     parent = ManyToOne()
    ...     children = parent.symmetrical
    
    >>> a, b, c = Foo('a'), Foo('b'), Foo('c')
    >>> b.parent = a
    >>> a.children.add(c)
    >>> b.parent, c.parent, a.children
    (a, a, set([c, b]))
    
    >>> b.parent = None
    >>> a.children
    set([c])
    '''

    @property
    def symmetrical(self):
        return self._symmetrical

    def __getitem__(self, key):
        return self.__get__(key)

    def __setitem__(self, key, value):
        self.__set__(key, value)

class ManyToOne(Relation):
    '''
    Many-to-one relation.
    
    The direct relation maps an object to a single other object. The 
    symmetrical mapping can be accessed from the ``symmetrical`` attribute
    of the ManyToOne relation, and it maps an object to the set of other 
    objects that points to it.
    '''

    def __init__(self, to_sources=None, to_destination=None, symmetrical=None):
        self.destination = {} if to_destination is None else to_destination
        self.sources = {} if to_sources is None else to_sources
        if symmetrical is None:
            self._symmetrical = OneToMany(to_sources=self.sources,
                                          to_destination=self.destination,
                                          symmetrical=self)
        else:
            self._symmetrical = symmetrical

    def __get__(self, obj, tt=None):
        if obj is None and isinstance(tt, type):
            return self
        return self.destination.get(id(obj), None)

    def __set__(self, obj, dest):
        id_obj = id(obj)
        if id_obj in self.destination:
            id_dest = id(self.destination[id_obj])
            siblings = self.sources[id_dest]
            siblings.discard(obj)

        self.destination[id_obj] = dest
        id_dest = id(dest)
        try:
            siblings = self.sources[id_dest]
        except KeyError:
            self.sources[id_dest] = siblings = relset(self.destination, self.sources, dest)
        siblings.add(obj)

    def __delete__(self, obj):
        raise AttributeError

class OneToMany(Relation):
    def __init__(self, to_sources=None, to_destination=None, symmetrical=None):
        self.destination = {} if to_destination is None else to_destination
        self.sources = {} if to_sources is None else to_sources
        if symmetrical is None:
            self._symmetrical = ManyToOne(to_sources=self.sources,
                                          to_destination=self.destination,
                                          symmetrical=self)
        else:
            self._symmetrical = symmetrical


    def __get__(self, obj, tt=None):
        if obj is None and isinstance(tt, type):
            return self
        try:
            return self.sources[id(obj)]
        except KeyError:
            sources = self.sources[id(obj)] = relset(self.destintation, self.sources, obj)
            return sources

    def __set__(self, obj, value):
        raise AttributeError

    def __delete__(self, obj):
        raise AttributeError

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=0)
