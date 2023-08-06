#-*- coding: utf8 -*-
from distutils.core import setup
import os

#===============================================================================
# Initialize configuration
#===============================================================================

# Program name
NAME = 'tutor'

# Save version file for documentation and for program
VERSION = '0.1'
with open(os.path.join('doc', 'source', 'VERSION'), 'w') as F:
    F.write(VERSION)
with open(os.path.join('src', 'tutor', 'version.py'), 'w') as F:
    F.write('VERSION = "%s"' % VERSION)

# Find all packages under the folder 'src/tutor'
PACKAGES = set(['tutor'])
for root, dirs, files in os.walk(os.path.join('src', 'tutor')):
    if '__init__.py' in files and not ('%s_' % os.path.sep in root):
        PACKAGES.add(root[4:].replace(os.path.sep, '.'))

# Write requirements.txt
REQUIRES = ['pyson', 'propertylib']
with open('requirements.txt', 'w') as F:
    F.write('%s\n%s' % (NAME, '\n'.join(REQUIRES)))

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
      packages=PACKAGES,
      requires=REQUIRES,
)
