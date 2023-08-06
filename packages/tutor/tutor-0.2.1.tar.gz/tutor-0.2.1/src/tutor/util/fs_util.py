import pyson
from pyson.json_encoding import register_cls, register
import fs.path
import fs.osfs
import fs.base
import fs.wrapfs
from fs.memoryfs import MemoryFS
from fs.tempfs import TempFS

def copy_fs(src, dest=None):
    '''Copy all contents in 'src' to 'dest' and return 'dest'.
    
    Parameters
    ----------
    src : fs.FS
        Source filesystem.
    dest : fs.FS or None
        Destination filesystem. If dest is None, it creates a new MemoryFS and
        returns it.
    '''

    if dest is None:
        dest = MemoryFS()
    elif isinstance(dest, basestring):
        dest = fs.osfs.OSFS(dest, create=True)
    if isinstance(src, basestring):
        src = fs.osfs.OSFS(src, create=True)

    for s_dir, files in src.walk():
        d_dir = dest.makeopendir(s_dir)
        s_dir = src.opendir(s_dir)
        for f in files:
            with d_dir.open(f, 'w') as F_in:
                with s_dir.open(f) as F_out:
                    F_in.write(F_out.read())

    return dest

def fsitems(fs_obj, mode='r'):
    '''
    Iterates over all files in the filesystem and yields (file_path, file) 
    pairs.
    '''
    for folder, files in fs_obj.walk():
        for fname in files:
            path = fs.path.join(folder, fname)
            yield (path, fs_obj.open(path, mode))

def filerotate(src, base='.', max_files=None):
    '''Rotate file names.
    
    In a group of files "src"-0, "src"-1, "src"-2, etc, it rotates the names
    making "src"-i => "src"-(i+1) so in the end it has a vacant slot to write
    "src"-0 (the "-0" suffix may be ommited).
    
    The ``filerotate`` function can be called in any function in the sequence
    of files and it tries to make room for this file by rotating only the 
    succeeding ones. The function also only makes a rotation when it is 
    necessary: if neither *src* or *src-0* does not exist, it does nothing,
    if a file *src-i* is missing it renames *src-(i-1)* to *src-i* and ends
    rotation.
    
    Examples
    -------
    
    In a directory with the following files::
    
      - file
      - file-1
      - file-2
      - file-4
      - file-5
    
    calling ``filerotate("file")`` will perform the following transformations::
    
      - file    => file-1
      - file-1  => file-2
      - file-2  => file-3
      - file-4  (does nothing)
      - file-5  (does nothing)
      
    Now the user is free to create "file-0" or "file" without risking 
    overwriting any file.
    
    It can be called from the middle of the sequence, e.g., 
    ``filerotate("file-4")`` will only modify "file-4" to "file-5" and "file-5" 
    to "file-6". ``filerotate("file-3")`` does nothing because "file-3" does 
    not exist.
    '''

    # Input check
    if max_files == 0:
        return
    if not isinstance(base, fs.base.FS):
        base = fs.osfs.OSFS(base)

    # Check if file do not exist (src and src-0 are equivalent) 
    basename, _, no = src.rpartition('-')
    if 'no' == '0' or not no:
        names = basename, '{0}-{1}'.format(basename, no)
        if all(not base.exists(x) for x in names):
            return
    else:
        if not base.exists(src):
            return

    # Chooses the new file name: src-n --> src-(n+1)
    try:
        no = (int(no) + 1 if no else 1)
    except ValueError:
        basename, no = src, 1
    dest = '{basename}-{no}'.format(basename=basename, no=no)

    # Rotate the new file, if it exists
    if base.exists(dest):
        max_files = (max_files - 1 if max_files is not None else None)
        filerotate(dest, base, max_files)

    # Move file
    if base.isfile(src):
        base.move(src, dest)
    elif base.isdir(src):
        base.move(src, dest)
    else:
        raise ValueError("'src' is neither a file or a directory")


@register_cls('tutor.SavingFS')
class SavingFS(TempFS):
    '''
    A filesystem that can saved as a JSON data structure. 
    '''
    def __init__(self):
        super(SavingFS, self).__init__()

    def _json_encode_(self):
        json = {}
        for k, v in fsitems(self):
            json[k] = v.read().encode('base64')
            v.close()
        return json

    @classmethod
    def _json_decode_(cls, json):
        new = cls()
        for k, v in json.items():
            new.makeopendir(fs.path.pathsplit(k)[0])
            with new.open(k, 'w') as F:
                F.write(v.decode('base64'))
        return new

    def __eq__(self, other):
        if isinstance(other, SavingFS):
            json1 = pyson.json_encode(self)
            json2 = pyson.json_encode(other)
            return not any(pyson.walkdiff(json1, json2))
        else:
            return False

    def __ne__(self, other):
        return not self == other

#===============================================================================
# Encoders/Decoders
#===============================================================================
def subfs_encoder(obj):
    return {'wrapped_fs': obj.wrapped_fs, 'sub_fs': obj.sub_fs}

def subfs_decoder(json):
    return json['wrapped_fs'].opendir(json['sub_fs'])

SubFS = type(fs.osfs.OSFS('/').opendir('tmp'))
register(SubFS, name='tutor.SubFS', encoder=subfs_encoder, decoder=subfs_decoder)

def osfs_encoder(obj):
    return {k: getattr(obj, k, d) for (k, d) in
            dict(root_path=None, thread_synchronize=True, encoding=None,
                 create=False, dir_mode=448, use_long_paths=True).items()}

def osfs_decoder(json):
    return fs.osfs.OSFS(**json)

register(fs.osfs.OSFS, name='tutor.OSFS', encoder=osfs_encoder, decoder=osfs_decoder)

# This module seems to fix a annoying bug that makes OSFS instances to 
# display errors on deletion when the tutor application is closed.
#
# Apparently, a None is being called, but after inspecting the code, the 
# reason for the error is not very clear.
# 
# The offending code is a method of fs.base.FS
#
# def __del__(self):
#    if not getattr(self, 'closed', True):
#            self.close()
#
# It throws a message as if close is None valued attribute, but it has been 
# defined as a method in the base class

from fs.base import FS

def new_del(self):
    try:
        if not getattr(self, 'closed', True):
            self.close()
    except Exception:
        pass

FS.__del__ = new_del

if __name__ == '__main__':
    with open('foo', 'w') as F:
        F.write('bar')

    filerotate('foo')

    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
