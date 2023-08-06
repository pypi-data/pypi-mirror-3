from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
if __name__ == '__main__':
    __package__ = b'tutor.bin' #@ReservedAssignment
    import tutor.bin #@UnusedImport

import sys
import json
import fs.path
import fs.errors
import fs.osfs
from fs.opener import fsopen
from ..permanence import savepath, openpath #@UnusedImport

def file_exists(fpath):
    '''Return True if file exists'''

    base, name = fs.path.split(fpath)
    base = fs.osfs.OSFS(base)
    return base.exists(name)

def assure_no_file(fpath, check=True):
    '''Assures there is no file with the given path'''

    if check and file_exists(fpath):
        raise ValueError('file already exists: %s' % fpath)

def with_ext(fname, ext):
    '''Returns the filename with extension'''

    if fname.endswith(ext):
        return fname
    else:
        return fname + ext

def without_ext(fname, ext):
    '''Returns the filename stripped from extension'''

    if fname.endswith(ext):
        return fname[:-len(ext)]
    else:
        return fname

def ext_pair(fname, ext=None):
    '''Returns a tuple (basename, ext) from the given filename'''

    if ext:
        return (without_ext(fname, ext), ext)
    else:
        fname, sep, ext = fname.rpartition('.')
        return (fname, sep + ext)

def as_unicode(st, encoding='utf8'):
    '''Encode string if it is not unicode'''

    if isinstance(st, unicode):
        return st
    else:
        return unicode(st, encoding)

def get_recent_files():
    '''Get a list of recent file names.'''

    try:
        with fsopen('~/.pytutor_recent') as F:
            return json.loads(F.read())
    except fs.errors.ResourceError:
        return {}

def set_recent(ftype, value):
    '''Set a file name as recent.'''

    recent = get_recent_files()
    recent[ftype] = value
    data = json.dumps(recent)
    with fsopen('~/.pytutor_recent', 'w') as F:
        F.write(data)

def main(parser):
    '''Decorates the main function'''

    def decorator(func):
        def main(argv=None):
            if argv is None:
                argv = sys.argv[1:]

            args = parser.parse_args(argv)
            args = vars(args)
            debug = args.pop('debug', False)
            for k, v in args.items():
                if v is None:
                    del args[k]
                elif isinstance(v, str):
                    try:
                        v.decode('ascii')
                    except UnicodeDecodeError:
                        args[k] = v.decode('utf8')
            try:
                func(**args)
            except Exception as ex:
                if debug:
                    raise
                else:
                    parser.error(unicode(ex))
        return main
    return decorator
