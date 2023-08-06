#-*- coding: utf8 -*-
from distutils.core import setup
import os

_CONFFUNCS = []
def conffunc(func):
    _CONFFUNCS.append(func)
    return func

def execconf():
    for func in _CONFFUNCS:
        func()

#===============================================================================
# Import FS and configure main directories
#===============================================================================
try:
    from fs.osfs import OSFS
    import fs.errors
except ImportError:
    print 'You must have the `fs` package installed. Type `pip install fs` if'
    print 'you have pip installed'
    raise SystemExit(1)
root_fs = fs.osfs.OSFS('.')

#===============================================================================
# Install the LaTeX pytutor package
#===============================================================================
#TODO: it works in Debian and derivatives w/ Texlive. It may not work in other
# distributions or configurations.

@conffunc
def set_texmf():
    try:
        texmf = OSFS('/usr/share/texmf/tex/latex/pytutor/', create=True)
        texmf_data = root_fs.getcontents('texmf/pytutor.sty')
        if texmf_data != texmf.getcontents('pytutor.sty'):
            os.chmod(texmf.getsyspath('/'), 755)
            texmf.setcontents('pytutor.sty', texmf_data)
            os.system('texhash')
            print 'pytutor.sty installed/updated successfully!'
    except (fs.errors.PermissionDeniedError, OSError):
        raise SystemExit('Permission denied: run as root in order to install pytutor.sty')

#===============================================================================
# Save consistent information across files
#===============================================================================
@conffunc
def set_version():
    data = 'VERSION = "%s"' % VERSION
    if data != root_fs.getcontents('src/tutor/version.py'):
        root_fs.setcontents('src/tutor/version.py', data)
    try:
        if data != root_fs.getcontents('doc/source/VERSION'):
            root_fs.setcontents('doc/source/VERSION', data)
    except:
        pass # not present in package distributions

@conffunc
def set_requirements():
    with open('requirements.txt', 'w') as F:
        F.write('%s>=%s' % (NAME, VERSION))
        for req in REQUIRES:
            name, _, version = req.partition('(')
            name, version = name.strip(), version.rstrip(')')
            F.write('\n%s%s' % (name, version))

#===============================================================================
# Compute packages and files that should go into distribution
#===============================================================================
@conffunc
def getpackages():
    packages = set(['tutor'])
    for root, dirs, files in os.walk(os.path.join('src', 'tutor')):
        if '__init__.py' in files and not ('%s_' % os.path.sep in root):
            packages.add(root[4:].replace(os.path.sep, '.'))
    PACKAGES[:] = packages

def sharefiles():
    '''List of files to go to /usr/share/pytutor'''
    result = []
    share = fs.osfs.OSFS('share')
    for dirname in share.walkdirs():
        dir = share.opendir(dirname)
        files = [ 'share/%s/%s' % (dirname[1:], f) for f in dir.listdir() if dir.isfile(f) ]
        if files:
            result.append(('/usr/share/pytutor' + dirname, files))
    return result

def scripts():
    '''List of script files'''
    return ['bin/%s' % f for f in root_fs.opendir('bin') ]

#===============================================================================
# Initialize configuration
#===============================================================================
NAME = 'tutor'
VERSION = '0.2.1'
REQUIRES = [('pyson (>=0.2)'), 'propertylib (>=0.1)', 'binpack (>=0.3)', 'fileslib (>=0.1)', 'fs (>=0.4)', 'plasTeX', 'jinja2']
PACKAGES = []
execconf()

#===============================================================================
# setup.py main configuration function
#===============================================================================
setup(name=NAME,
      version=VERSION,
      description='Creates and organizes randomized questions and exams.',
      author='Fábio Macêdo Mendes',
      author_email='fabiomacedomendes@gmail.com',
      url='code.google.com/p/py-tutor',
      long_description=(
'''Tutor is a system for creating and organizing questions and exams that can 
be randomized. The project focus in the needs of maths teachers. Questions can 
be created in LaTeX and it has support for many algebra/math systems such as 
Sympy, Maple, Mathematica, Matlab, etc.'''),

      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
      package_dir={ '': 'src' },
      data_files=[('/etc', ['etc/pytutor.conf'])] + sharefiles(),
      scripts=scripts(),
      packages=PACKAGES,
      requires=REQUIRES,
)
