import os
import fs.tempfs

__all__ = ['lyxtotex']

def lyxtotex(lyx_f):
    '''Read LyX data on file descriptor ``lyx_f`` and return a file descriptor 
    with the same data converted to LaTeX'''

    base = fs.tempfs.TempFS()
    with base.open('main.lyx', 'w') as F:
        F.write(lyx_f.read())

    # Command to convert lyx to tex
    #cmd = 'lyx -f -e latex main.lyx &> /dev/null'
    cmd = 'lyx -f -e latex main.lyx' # redirecting stderr creates bug!
    olddir = os.getcwd()
    try:
        os.chdir(base.getsyspath(''))
        os.system(cmd)
        result = base.open('main.tex')
    finally:
        os.chdir(olddir)

    return result
