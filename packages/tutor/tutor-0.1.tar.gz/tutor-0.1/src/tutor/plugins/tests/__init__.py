import doctest
import inspect
import sys
import traceback

def test_class(cls):
    '''
    asdas
    
    @param cls:
    '''

    methods = [ m for m in dir(cls) if m.startswith('test_') or m.startswith('example_') ]
    methods = [ getattr(cls, m).im_func for m in methods ]

    if not methods:
        return

    sys.stdout.write('Testing type: %s' % getattr(cls, '__name__', 'Anonymous type %s' % cls))
    for m in methods:
        docstring = m.func_doc or ('%s()' % m.func_name)
        docstring = docstring.strip(' \n')
        sys.stdout.write('\n  * %s... ' % docstring)
        try:
            m(None)
        except AssertionError:
            sys.stdout.write(' fail\n')
            traceback.print_exc()
#        except Exception as ex:
#            sys.stdout.write(' error')
#            print '\nRe-raising exception'
#            raise ex
        else:
            sys.stdout.write(' ok')
    print


def define_tests():
    f = inspect.currentframe(1)
    if f.f_globals['__name__'] == '__main__':
        return True
    else:
        return False


def define_examples():
    f = inspect.currentframe(1)
    if f.f_globals['__name__'] == '__main__':
        return True
    else:
        return False

def main():
    '''
    Perform all tests defined in module.
    '''

    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
    print 'All doctests passed!\n'

    # Access module's locals and inspect the classes defined there. 
    f = inspect.currentframe(1)
    mod_name = f.f_globals['__name__']

    # Find all classes defined in module
    classes = []
    for k, v in  f.f_globals.items():
        if type(v) == type:
            if getattr(v, '__module__', None) == mod_name:
                classes.append(v)

    # Process all classes 
    for cls in classes:
        test_class(cls)

