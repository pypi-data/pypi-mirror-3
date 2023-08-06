import collections

class IdList(collections.MutableSequence, list):
    '''A list whose members have an `id` attribute. List's items can be 
    retrieved either by index or by id or index.  
    
    This class assumes that the `id` never changes in the member items. It also
    guarantees that no members exist with the same `id`.
    
    First create a class whose instances have an `id` attribute. 
    
    >>> class Foo(object):
    ...     def __init__(self, id):
    ...         self.id = id
    ...     def __repr__(self):
    ...         return 'Foo(%r)' % self.id
    
    An IdList can be filled with, e.g., Foo() instances
    
    >>> lst = IdList([Foo('first'), Foo('second')])
    >>> lst[0], lst['second']
    (Foo('first'), Foo('second'))
    
    An object that does not have an `id` attribute cannot be added
    
    >>> lst.append('some string')
    Traceback (most recent call last):
    ...
    AttributeError: 'str' object has no attribute 'id'
    '''

    def __init__(self, iterable):
        list.__init__(self)
        self._idmapping = {}
        for obj in iterable:
            self.append(obj)

    def __delitem__(self, idx):
        if not isinstance(idx, int):
            try:
                idx = self._idmapping[idx]
            except KeyError:
                raise IndexError(idx)
        item_id = list.__getitem__(self, idx).id
        list.__delitem__(self, idx)
        del self._idmapping[item_id]

    def __getitem__(self, idx):
        try:
            return list.__getitem__(self, idx)
        except TypeError:
            return self.getfromid(idx)

    def __setitem__(self, idx, value):
        print idx, value
        value_id = value.id
        if value_id in self._idmapping:
            raise ValueError('object with id %s already exists' % value_id)
        list.__setitem__(self, idx, value)
        try:
            self._idmapping[value_id] = idx
        except TypeError: # non-hashable types
            list.__delitem__(idx)
            raise TypeError("non-hashable id type: '%s'" % type(value_id))

    def __contains__(self, obj):
        try:
            idx = self._idmapping[obj.id]
        except (AttributeError, KeyError):
            return False
        else:
            return list.__getitem__(self, idx) == obj

    def insert(self, idx, value):
        value_id = value.id
        try:
            hash(value_id) # assert id is hashable
        except TypeError:
            list.__delitem__(idx)
            raise TypeError("non-hashable id type: '%s'" % type(value_id))
        if value_id in self._idmapping:
            raise ValueError('object with id %s already exists' % value_id)

        size = len(self)

        # Insert item in list
        if idx < size:
            list.insert(self, idx, value)
            getter, idmapping = list.__getitem__, self._idmapping
            idmapping[value_id] = idx

            for idx in range(idx, size - idx):
                idmapping[getter(idx).id] = idx

        # Append
        elif size == idx:
            self._idmapping[value_id] = idx
            list.append(self, value)

        # Too large list
        else:
            raise IndexError('list index out of range')

    __len__ = list.__len__

    def hasid(self, item_id):
        '''Checks if list has an object with a given id.'''

        return item_id in self._idmapping

    def getfromid(self, item_id):
        '''Retrieves the object in list with the given id.'''
        try:
            idx = self._idmapping[item_id]
        except KeyError:
            raise ValueError('no items with id: %r' % item_id)
        return list.__getitem__(self, idx)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
