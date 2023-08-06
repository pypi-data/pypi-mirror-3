import copy
import csv
import datetime
import functools
import os
from tutor import SETTINGS

#===============================================================================
# Global configurations
#===============================================================================

# Update paths
PATHS = SETTINGS.setdefault('LibPath', {})
ROOT_PATH = PATHS.setdefault('root', '/var/lib/tutor')
UROOT_PATH = PATHS.setdefault('user_root', os.path.expanduser('~/.local/lib/tutor'))
LEARNING_OBJ_PATH = PATHS.setdefault('learning_obj', os.path.join(ROOT_PATH, 'learning_obj'))
ULEARNING_OBJ_PATH = PATHS.setdefault('user_learning_obj', os.path.join(UROOT_PATH, 'learning_obj'))
EXAM_OBJ_PATH = PATHS.setdefault('exam', os.path.join(ROOT_PATH, 'exam'))
UEXAM_OBJ_PATH = PATHS.setdefault('user_exam', os.path.join(UROOT_PATH, 'exam'))
STUDENT_OBJ_PATH = PATHS.setdefault('student', os.path.join(ROOT_PATH, 'student'))
USTUDENT_OBJ_PATH = PATHS.setdefault('user_student', os.path.join(UROOT_PATH, 'student'))

# Valid classes
VALID_CLASSES = [ key for key in PATHS if not key.startswith('user_') ]
del VALID_CLASSES[VALID_CLASSES.index('root')]

#===============================================================================
# Directory and file manipulation classes
#===============================================================================
class RawLibDir(object):
    def __init__(self, path, section_t={}):
        '''
        Object that represents a directory in the file system.
        
        The difference from regular directories is that RawLibDir objects have
        a 'section_t' parameter that describes the hierarchy of file types in
        the given directory. By default, it reads the section type hierarchy 
        information from the .dirconfig file.
        
        The parameter 'section_t' is a dictionary of the form 
            { section_name : sequence of types }
        '''

        # Checks if directory exists
        self.path = os.path.abspath(path)
        if not os.path.exists(self.path):
            raise IOError(2, 'file not found', path)

        # Check if path is in global section_t information mapping
        self.section_t = self.REGISTERED_SECTIONS.get(path, self.DEFAULT_SECTION_T)

        # Read .dirconfig
        try:
            with open(os.path.join(self.path, '.dirconfig')) as F:
                cfg = csv.reader(F)
                cfg = dict((row[0], row[1:]) for row in cfg)
        except IOError:
            cfg = {}

        # Update sections
        self.update_sections(cfg)
        self.update_sections(section_t)

    def subdir(self, subdir, *args):
        '''
        dir.subdir('sub1', 'sub2', ...) walks to sub-directory 'sub1/sub2/...'
        of dir, if it exists. 
        '''

        if args:
            return self.subdir(subdir).subdir(*args)
        else:
            return RawLibDir(os.path.join(self.path, subdir), self.section_t)

    def __str__(self):
        return '<RawLibDir %s>' % self.path

    def _listdir(self):
        '''
        Return a list of strings representing the paths of files and directories 
        in RawLibDir.
        '''
        J = os.path.join
        R = self.path
        return [ J(R, p) for p in os.listdir(self.path) if p != '.dirconfig' ]

    def subdirs(self):
        '''
        Return a list of RawLibDir instances representing the sub-directories in 
        RawLibDir.
        '''

        typeH = self.section_t
        subdirs = [ p for p in self._listdir() if os.path.isdir(p) ]
        return [ RawLibDir(p, typeH) for p in subdirs ]

    def files(self):
        'Return a list of paths for each file in directory'

        return [ p for p in self._listdir() if os.path.isfile(p) ]

    def update_sections(self, dic):
        '''
        Update the section_t dictionary with information of the new dictionary.
        '''
        for section, tlist in dic.items():
            tlist = list(tlist)
            tset = set(tlist)
            for type in self.section_t.get(section, []):
                if type not in tset:
                    tlist.append(type)

            self.section_t[section] = tlist

    #===========================================================================
    # Dictionaries for section_t configuration
    #===========================================================================
    DEFAULT_SECTION_T = {
        'root': ['json'],
    }

    SECTION_T_LEARNING_OBJ = {
        'root': ['json', 'lyx', 'tex'],
        'namespace': ['json', 'python', 'maple', 'lyx', 'tex', 'yaml'],
    }

    REGISTERED_SECTIONS = {
        LEARNING_OBJ_PATH: SECTION_T_LEARNING_OBJ,
        ULEARNING_OBJ_PATH: SECTION_T_LEARNING_OBJ,
    }


#===============================================================================
# Directory in the lib filesystem
#===============================================================================
class LibDir(RawLibDir):
    def __init__(self, *path, **kwds):
        '''
        Object that behaves as a directory in the library. It scans 
        simultaneously for directories in the user and sys directories in the 
        library. 
        
        The default implementation assu
        @param path:
        @param section_t:
        '''

        section_t = kwds.pop('section_t', {})
        self.path = path
        if kwds:
            raise TypeError("Invalid keyword argument, '%s'" % (iter(kwds.next())))

        # Save root class
        self.obj_class = self.path[0]
        if self.obj_class not in VALID_CLASSES:
            raise ValueError("'invalid root path, '%s'" % self.obj_class)

        # Store the separate sys and user directories
        try:
            root = RawLibDir(PATHS['user_' + self.obj_class])
        except IOError as ex1:
            self.user_dir = None
        else:
            self.user_dir = root.subdir(*self.path[1:])
            self.user_dir.update_sections(section_t)
        try:
            root = RawLibDir(PATHS[self.obj_class])
        except IOError as ex2:
            self.sys_dir = None
        else:
            self.sys_dir = root.subdir(*self.path[1:])
            self.sys_dir.update_sections(section_t)

        if self.sys_dir is None and self.user_dir is None:
            raise IOError("%s and '%s'" % (ex1, ex2.filename))

    def subdir(self, root, *args):
        if args:
            return super(LibDir, self).subdir(root, *args)
        else:
            new = object.__new__(LibDir)
            new.path = copy.deepcopy(self)
            new.user_dir = new.sys_dir = None
            if self.user_dir is not None:
                try:
                    new.user_dir = self.user_dir.subdir(root)
                except IOError as ex:
                    pass
            if self.sys_dir is not None:
                try:
                    new.sys_dir = self.sys_dir.subdir(root)
                except IOError as ex:
                    pass
            if new.sys_dir is None and new.user_dir is None:
                raise IOError(ex)
            return new

    @property
    def section_t(self):
        if self.user_dir:
            return self.user_dir.section_t
        else:
            return self.sys_dir.section_t

    def get_section_t(self, location):
        '''
        Return section_t object from user or sys locations
        '''
        if location == 'user':
            return getattr(self.user_dir, 'section_t', {})
        elif location == 'sys':
            return getattr(self.sys_dir, 'section_t', {})
        else:
            raise ValueError('invalid location, %s' % location)

    def _listdir(self):
        l1 = getattr(self.user_dir, '_listdir', lambda: [])()
        l2 = getattr(self.sys_dir, '_listdir', lambda: [])()
        return l1 + l2

#===============================================================================
# Class representing nodes in the Lib filesystem
#===============================================================================
class file_tt(file):
    def __init__(self, fpath, type, mode='r', buffering=None):
        '''
        A file-like object with an additional type attribute
        '''

        self.type = type
        args = (() if buffering is None else (buffering,))
        super(file_tt, self).__init__(fpath, mode, *args)

class LibNode(object):
    def __init__(self, *path):
        '''
        Class representing nodes in the Lib filesystem
        '''

        # Save input
        basedir = LibDir(*path[:-1])
        if basedir.user_dir is None:
            self._basedir = basedir.sys_dir
        else:
            self._basedir = basedir.user_dir
        self.name = path[-1]

        # Check if object path points to a directory
        basename = os.path.join(self._basedir.path, self.name)
        self.isdir = False
        self._sections = {}
        if os.path.exists(basename + '.lobj') and os.path.isdir(basename + '.lobj'):
            basename += '.lobj'
            self.isdir = True
            fnames = os.listdir(basename)
            fpaths = [ os.path.join(basename, f) for f in fnames ]
            sections = set([ f.split('.')[0] for f in fnames ])
            for section in sections:
                files = [ fp for (fp, fn) in zip(fpaths, fnames) if fn.startswith(section) ]
                self._sections[section] = self._make_tt_files_list(files, section)
        else:
            files = [ f for f in self._basedir.files() if os.path.basename(f).startswith(self.name) ]
            if not files:
                raise IOError("no file named '%s.*' in '%s'" % (self.name, self._basedir.path))

            # Save list of (types, fpath) priorities for given section
            self._sections['main'] = self._make_tt_files_list(files, 'main')

    def _make_tt_files_list(self, files, section):
        # Object is a single file. Check of which type and assign this file
        # name to the 'main' section

        file_types = map(self._get_file_type_by_ext, map(lambda x: os.path.splitext(x)[1], files))

        # Map types to files and assure that no type is associated with more 
        # than one file 
        file_map = {}
        for f, tt in zip(files, file_types):
            if not tt in file_map:
                file_map[tt] = f
            else:
                raise ValueError("repeated files of type %s: '%s' and '%s'" % (tt, f, file_map[tt]))

        # Reorder files/types list using with information on section_t
        file_list = []
        for tt in self._basedir.section_t.get(section, []):
            fpath = file_map.pop(tt)
            if fpath is not None:
                file_list.append(tt, fpath)
        file_map = file_map.items()
        file_map.sort() # sort the remaining types alphabetically
        file_list.extend(file_map)

        return file_list

    @property
    def sections(self):
        return list(self._sections)

    def _get_file_type_by_ext(self, ext):
        # For now, it only removes the leading dot from the extension
        return ext[1:]

    def _section_vectorize(func): #@NoSelf
        @functools.wraps(func)
        def decorated(self, section=None, *args, **kwds):
            if section is None:
                getter = lambda x: func(self, x, *args, **kwds)
                return dict((s, getter(s)) for s in self.sections)
            else:
                return func(self, section, *args, **kwds)
        return decorated

    @_section_vectorize
    def open(self, section=None, type=None, mode='r'):
        '''
        Open a the resource of a given type in a given section.
        
        Arguments
        --------- 
        section : str
            Section name. If section is None, the function return a list with 
            all files in all sections.
        type : str
            File type. Usually it is the same as the file extension.
        mode : str
            (r)ead (w)rite or (a)ppend mode for opening the file object.
            
        Output
        ------
        A file-like object with a 'type' attribute    
            
        Observations
        ------------
        It is up to the user to close the returning file object.
        
        '''

        tt_fpaths = self._get_tt_fpaths(section)
        if type is None:
            tt, fpath = tt_fpaths[0]
            return file_tt(fpath, tt, mode)
        else:
            for tt, fpath in tt_fpaths:
                if tt == type:
                    return file_tt(fpath, tt, mode)
            else:
                raise ValueError('no file of type %s is available' % type)

    @_section_vectorize
    def get_time(self, section=None):
        '''
        Return a float representing the modification time of the main file in a
        given section.
        '''
        tt_fpaths = self._get_tt_fpaths(section)
        fpath = tt_fpaths[0][1]
        return os.stat(fpath).st_mtime

    @_section_vectorize
    def get_datetime(self, section=None):
        '''
        Return a datetime object representing the modification time of the main 
        file in a given section.
        '''
        return datetime.datetime.fromtimestamp(self.get_time(section))

    @_section_vectorize
    def _get_tt_fpaths(self, section=None):
        '''
        Return a list of (type, fpath) tuples for all files in a given section. 
        '''
        try:
            return self._sections[section]
        except KeyError:
            raise ValueError('section %s is empty' % section)

    @_section_vectorize
    def get_type(self, section=None):
        '''
        Return the type of the main file in a given section.
        '''
        tt_fpaths = self._get_tt_fpaths(section)
        return tt_fpaths[0][0]

    @_section_vectorize
    def get_fpath(self, section=None):
        '''
        Return the path to the main file in a given section.
        '''
        tt_fpaths = self._get_tt_fpaths(section)
        return tt_fpaths[0][1]

    def delete(self, section=None, type=None):
        '''
        Delete all files with the given type and section.
        '''

        for sec, tt_fpaths in self._section.items():
            if section is None or sec == section:
                for tt, fpath in tt_fpaths:
                    if type is None or tt == type:
                        os.unlink(fpath)


if __name__ == '__main__':
    d = LibDir('exam', 'examples')
    print(d.sys_dir.section_t)
    print(d.section_t)
    print(map(str, d.subdirs()))
    print(d.files())

    n = LibNode('exam', 'examples', 'simple_exam')
    print(n.sections)
    with n.open('main') as F:
        print(F.type)
        print(F.read())
    print(n.get_type('main'))
    print(n.get_type())
    print(n.get_datetime())

    n = LibNode('learning_obj', 'examples', 'namespace')
    print(n._sections)
#    import doctest
#    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
