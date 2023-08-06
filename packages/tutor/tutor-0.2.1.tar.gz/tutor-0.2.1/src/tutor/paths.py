'''
This module defines the special paths in the ``Py-Tutor`` system may search for 
files.

Apart from Python code, the ``Py-Tutor`` system may use several data files. 
Some of these files are available system-wide and others are specific to each 
user. In this section, we describe the directory organization employed in the
whole system. All paths are exported as PyFileSystem constants in the module 
mod:`tutor.paths`. 

System-wide paths
-----------------

These  store data files that are necessary in order to Tutor to perform its
basic functions.   

 SYSTEM_CONFIG_FILE:
   /etc/pytutor.conf: is .ini configuration file with system wide 
   settings.
 
 SYSTEM_BIN_DIR:
   /usr/bin/: This is where the executable files and scripts are stored. 
   
 SYSTEM_DATA_DIR:
   /usr/share/pytutor/: a directory that stores all necessary data files such 
   as templates, examples, etc. 
'''

from fs.osfs import OSFS
from tutor.settings import read_global_settings, read_local_settings, SETTINGS

# Read settings files and prepare other paths
SYSTEM_CONFIG_DIR = OSFS('/etc/')
SYSTEM_CONFIG_FILE = SYSTEM_CONFIG_DIR.getsyspath('pytutor.conf')
LOCAL_CONFIG_DIR = OSFS('~/.config/')
LOCAL_CONFIG_FILE = LOCAL_CONFIG_DIR.getsyspath('pytutor.conf')
read_global_settings(SYSTEM_CONFIG_FILE)
read_local_settings(LOCAL_CONFIG_FILE)
SYSTEM_CONFIG_DIR = SYSTEM_CONFIG_DIR.getsyspath('')
LOCAL_CONFIG_DIR = LOCAL_CONFIG_DIR.getsyspath('')

# Retrieve system read-only paths from SETTINGS
SYSTEM_BIN_DIR = unicode(SETTINGS['system_path::bin'])
SYSTEM_DATA_DIR = OSFS(SETTINGS['system_path::data'])
SYSTEM_TEMPLATES_DIR = SYSTEM_DATA_DIR.getsyspath('templates')
SYSTEM_EXAMPLES_DIR = SYSTEM_DATA_DIR.getsyspath('examples')
SYSTEM_DATA_DIR = SYSTEM_DATA_DIR.getsyspath('')

# Retrieve user-local paths from SETTINGS 
LOCAL_LIBRARY_DIR = OSFS(SETTINGS['content_path::library'], create=True)
LOCAL_LIBRARY_DIR = LOCAL_LIBRARY_DIR.getsyspath('')
LOCAL_CLASSES_DIR = OSFS(SETTINGS['content_path::classes'], create=True)
LOCAL_CLASSES_DIR = LOCAL_CLASSES_DIR.getsyspath('')

del OSFS
__all__ = [ p for p in globals().keys() if p.isupper() ]
