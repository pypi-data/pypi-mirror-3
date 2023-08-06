'''
Created on 08/05/2012

@author: chips
'''
from __future__ import print_function

'''``Py-Tutor`` uses the commonly used ``.ini`` file format in its 
configuration files. There are two configuration files understood by the system:
a global configuration file in ``/etc/pytutor.conf`` and a local configuration 
file in ``$HOME/.config/pytutor.conf``.

Some options (like system-wide paths) can only be defined in the global 
configuration file and other options are excluslive of the local configuration 
file. The user defined configurations will always override the global ones when 
both are supported.

Internal representation
=======================

``.ini`` files are composed by sections, keys and values. When loaded, this 
structure is converted to a dictionary of { "section::key": "value" } which
is accessible from ``tutor.settings.SETTINGS``, ``tutor.settings.GLOBAL_SETTINGS``, 
or ``tutor.settings.LOCAL_SETTINGS``.

Configuration fields
====================

The global configuration has a "system_path" section which should not be present
in the local configuration. All other sections are common to both files.

  "system_path"
    bin: directory that has the Py-Tutor executables
    data: directory that contains template data
  
  "content_path"
    library: base path where question and exam files are stored 
    classes: base path where classroom files stored
    
  "internationalization" (not supported yet)
    language: a valid language code string (e.g., en, en-US, pt-BR, etc) 
'''
import ConfigParser

#===============================================================================
# Creates universal SETTINGS dictionary
#===============================================================================
def _update_settings():
    '''Update the SETTINGS variable from the GLOBAL_SETTINGS and LOCAL_SETTINGS
    dictionaries'''

    # Wipe dictionary
    for k in SETTINGS.keys():
        del SETTINGS[k]

    # Update
    SETTINGS.update(GLOBAL_SETTINGS)
    SETTINGS.update(LOCAL_SETTINGS)

#===============================================================================
# Dictionary holding settings data
#===============================================================================
GLOBAL_SETTINGS_DEFAULT = {
  'system_path::bin': '/usr/bin/',
  'system_path::data': '/usr/share/pytutor/',
  'content_path::library': '~/.local/share/pytutor/lib',
  'content_path::classes': '~/.local/share/pytutor/classes',
}
LOCAL_SETTINGS_DEFAULT = {
  'content_path::library': '~/.local/share/pytutor/lib',
  'content_path::classes': '~/.local/share/pytutor/classes',
}

SETTINGS = {}
GLOBAL_SETTINGS = GLOBAL_SETTINGS_DEFAULT.copy()
LOCAL_SETTINGS = LOCAL_SETTINGS_DEFAULT.copy()

#===============================================================================
# Functions for reading configuration files
#===============================================================================
def _read_conf_file(fname):
    '''
    Read configuration file and return the dictionary structure associated 
    with it.
    
    >>> conf = _read_conf_file('/etc/pytutor.conf')
    >>> conf_keys = list(conf)
    >>> conf_keys.sort(); conf_keys[:2]
    [u'content_path::classes', u'content_path::library']
    '''

    # Create config dict
    config = ConfigParser.SafeConfigParser()
    config.read(fname)
    settings_dict = {}
    for section in config.sections():
        for key, value in config.items(section):
            settings_dict[u'%s::%s' % (section.strip(), key)] = value

    return settings_dict

def read_global_settings(fname):
    '''
    Read global config file and update GLOBAL_SETTINGS and SETTINGS variables.
    '''

    settings = _read_conf_file(fname)
    #TODO: validate and fill in the blanks
    GLOBAL_SETTINGS.update(settings)
    _update_settings()

def read_local_settings(fname):
    '''
    Read local config file and update LOCAL_SETTINGS and SETTINGS variables.
    '''

    settings = _read_conf_file(fname)
    #TODO: validate and fill in the blanks
    LOCAL_SETTINGS.update(settings)
    _update_settings()

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
