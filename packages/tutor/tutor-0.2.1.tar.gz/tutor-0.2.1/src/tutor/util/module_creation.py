'''
Creates modules from a string of Python code.

This is used in question.namespace for a fast executing of namespace.py code.
'''
from cStringIO import StringIO
from fs.expose.importhook import FSImportHook
from fs.memoryfs import MemoryFS
from fs.base import FS
import random
import string
import sys

__all__ = [ 'new_module', 'setup_module', 'get_module_from' ]
# Allowed characters in valid Python names
# One must also prevent names from starting with digits     
MOD_CHAR_NAMES = string.ascii_letters + string.digits + '_'

# Gives 63**10 ~ 10**17  unique names
MOD_RAND_NAME_LENGTH = 15 # approx

# Black list used names (even though chances of repetitions are very slim)
MOD_NAMES = set([None])

# Default root module name
MOD_NAME_DEFAUT_ROOT = '.'.join(__name__.split('.')[:-1] + ['user_modules']) + '.M'

def new_mod_name(root=None):
    '''
    Returns a random unique module name under the given root. 
    '''

    # Make local variables and default values 
    if root is None:
        root = MOD_NAME_DEFAUT_ROOT
    choice, good_chars = random.choice, MOD_CHAR_NAMES

    # Loop until it finds a unique value (which is probably in the first 
    # iteration, by the way...)
    while True:
        rand_name = ''.join(choice(good_chars) for _ in range(MOD_RAND_NAME_LENGTH))
        name = root + rand_name
        if name not in MOD_NAMES:
            MOD_NAMES.add(name)
            return name

def as_file(obj, coding='utf8'):
    '''
    Expose unicode and byte strings as file-like objects. If argument is 
    already a file-like object, it is simply returned to the caller. 
    '''

    if isinstance(obj, unicode):
        obj = obj.encode(coding)
    if isinstance(obj, str):
        obj = StringIO(obj)

    if hasattr(obj, 'read'):
        return obj
    else:
        raise TypeError('must be a file-like object, got %s' % type(obj))

def gen_fs_object(mod_data, root, coding, pyc, pyo):
    '''
    Creates MemoryFS object to be passed to setup_module()
    '''
    # Check pyo and pyc parameters
    if pyo or pyc:
        raise NotImplemented('bytecode not yet interpreted')

    # Creates a file structure that describes a module
    if not hasattr(mod_data, 'items'):
        ext = ('pyo' if pyo else ('pyc' if pyc else 'py'))
        root = root.split('.')
        root[-1] = '%s.%s' % (root[-1], ext)
    else:
        root = root.split('.')

    # Creates a package file structure
    fs_data = curr_dir = {}
    while root:
        subdir = root.pop(0)
        curr_dir = curr_dir.setdefault(subdir, {} if root else mod_data)

    # Creates the package FS structure
    init = set(['__init__.py', '__init__.pyc', '__init__.pyo'])
    def fill_fs(fs, node):
        # Creates __init__.py files on directories, if they do not exist
        if not init.intersection(node):
            fs.setcontents('__init__.py', '')

        # Fills all defined files and subdirectories
        for dir, sub_node in node.items():
            if hasattr(sub_node, 'items'):
                fs.makedir(dir)
                sub_fs = fs.opendir(dir)
                fill_fs(sub_fs, sub_node)
            else:
                fs.setcontents(dir, as_file(sub_node))
    fs = MemoryFS()
    fill_fs(fs, fs_data)
    return fs

def setup_module(mod_data, root=None, coding='utf8', pyc=False, pyo=False):
    r'''Creates a Python module or package and return its sys.modules path.
    
    Arguments
    ---------
    
    mod_data : string, bytes, dict or FS
        Object holding data in module/package.
    root : string
        Fully qualified name for the module/package. If root is None, a random
        name is choosen and the module is saved in "modules.<some_name>". "root"
        paths can also end with a "?". In that case, the interrogation mark 
        is replaced by a random unique name. 
    coding : string
        Encoding for saving data from unicode strings.
    pyc, pyo : bool
        If mod_data is a bytes object, pyc and pyo parameters are used to tell 
        the interpreter that data is compiled python bytecode.   
    
    Example
    -------
    
    The modules can be defined as strings of Python code or bytecode
    
    >>> foo = ('QUESTION = "What is the ultimate question of life, ' 
    ...        'the universe, and everything?"')
    >>> bar = 'def answer():\n   return 42'
    
    The package directory structure is emulated by dictionaries. One does not 
    need to append empty __init__.py files explicitly.
    
    >>> package = {'important': {'foo.py': foo, 'bar.py': bar}}
    >>> mod_name = setup_module(package, root='foobar')
    
    This represent the package
    
    -- foobar/
     |-- __init__.py
     \-- important/
       |-- __init__.py
       |-- foo.py
       \-- bar.py
    
    The submodules foo and bar can be retrieved using the get_module_from()
    function or the standard Python mechanisms
     
    >>> foo = get_module_from('foobar.important.foo')
    >>> from foobar.important import bar
    >>> print(foo.QUESTION)
    What is the ultimate question of life, the universe, and everything?
    >>> print(bar.answer())
    42
    '''

    # Pick up module name
    if root is None or root.endswith('?'):
        root = root and root[:-1]
        root = new_mod_name(root)

    # Create FS object
    if not isinstance(mod_data, FS):
        fs = gen_fs_object(mod_data, root, coding, pyc, pyo)
    else:
        fs = mod_data

    # Creates module from import_hook
    mod = FSImportHook(fs)
    sys.meta_path.append(mod)
    return root

def new_module(mod_data, root=None, coding='utf8', pyc=False, pyo=False):
    '''
    Similar to setup_module(), but returns the loaded module instead of
    the Python path to the module.
    
    Examples
    --------
    
    Defines the souce code for the module.
    
    >>> src = 'print("module is starting...")'
    
    With setup_module(), the module is only executed after get_module_from() is 
    explicitly called
    
    >>> mod_name = setup_module(src)
    >>> mod = get_module_from(mod_name)
    module is starting...
    
    With new_module(), the module is executed right away
    
    >>> mod = new_module(src)
    module is starting...
    '''

    mod_path = setup_module(mod_data, root, coding, pyc, pyo)
    return get_module_from(mod_path)

def get_module_from(mod_path):
    '''
    Loads and return the module in the given mod_path
    
    Examples
    --------
    
    >>> get_module_from('math')
    <module 'math' (built-in)>
    
    >>> mod = get_module_from('os.path')
    >>> mod.splitext('foo.bar') # same as os.path.splitext
    ('foo', '.bar')
    '''
    module = __import__(mod_path)
    sub_modules = mod_path.split('.')[1:][::-1]
    while sub_modules:
        module = getattr(module, sub_modules.pop())
    return module

if __name__ == '__main__':
    MOD_NAME_DEFAUT_ROOT = 'user_modules.M'

    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
