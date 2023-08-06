#-*- coding:utf8 -*-
import functools
import collections
def is_filter(func):
    func.is_filter = True
    return func

#===============================================================================
#         Dictionary that maps types to converters in module namespace
#===============================================================================
TYPE_TO_CONVERTER = {}

@is_filter
def latex(obj, **kwds):
    '''Returns a latex representation of 'obj'.'''

    # use the worker from the type hierarchy
    types = type(obj).mro()
    result = None
    for tt in types:
        worker = TYPE_TO_CONVERTER.get(tt, None)
        if worker is not None:
            result = worker(obj, **kwds)
            break

    # type must be recognized
    if result is None:
        raise TypeError('type not recognized, {0}'.format(type(obj)))

    # post-process result
    return result

def latex_register(tt, converter=None):
    '''Register type 'tt' to work with conversion function. Can also be used as
    a generator:
    
    >>> @latex_register(tt)
    >>> def worker(obj, **kwds):
    >>>    # --- do something useful ---
    >>>    return str(obj) 
    
    Arguments
    ---------
    
    tt: type
        Type that accepts conversion to latex output
        
    converter: function
        Converter function.
    
    Output
    ------
    
    None
    '''

    if converter is None:
        return functools.partial(latex_register, tt)
    else:
        TYPE_TO_CONVERTER[tt] = converter
        return converter

#===============================================================================
#                                 Converters
#===============================================================================
@latex_register(long)
@latex_register(complex)
@latex_register(float)
@latex_register(int)
@latex_register(basestring)
def unicode_worker(obj, **kwds):
    return unicode(obj)

@latex_register(tuple)
def tuple_worker(obj, **kwds):
    latex_list = (latex(item) for item in obj)
    latex_list = ', '.join(latex_list)
    return u'\\left( {0} \\right)'.format(latex_list)

@latex_register(list)
def list_worker(obj, **kwds):
    latex_list = (latex(item) for item in obj)
    latex_list = ', '.join(latex_list)
    return u'\\left[ {0} \\right]'.format(latex_list)

@latex_register(dict)
def dict_worker(obj, **kwds):
    items_list = ((latex(k), latex(v)) for k, v in obj.items())
    items_list = ('%s: %s' % item for item in items_list)
    items_list = ', '.join(items_list)
    return u'\\left{{ {0} \\right}}'.format(items_list)

@latex_register(object)
def fallback_worker(obj, **kwds):
    if isinstance(obj, collections.Mapping):
        return dict_worker(obj, **kwds)
    elif isinstance(obj, collections.Iterable):
        return tuple_worker(obj, **kwds)
    else:
        return unicode_worker(obj, **kwds)

if __name__ == '__main__':
    print latex('ada sdasaá')
    print latex(1)
    print latex(1.233)
    print latex([1.233, 2, ('a', 2)])
    print latex(set((1, 2, 3)))
    print latex({1:2, 2:[2, 3]})
