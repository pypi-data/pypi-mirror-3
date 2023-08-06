from __future__ import print_function
import os
import itertools
import ConfigParser
VERSION = { 'major': 0, 'minor': 1, 'tail': 'pre-alpha' }

SETTINGS_STRUCTURE = [
    ('LibPath', (
         'root',
         'user_root',
         'learning_obj',
         'user_learning_obj',
         'exam',
         'user_exam',
         'student',
         'user_student',
        )
    ),
    ('Database', (
         'path',
        )
    ),
    ('Templates', (
         'path',
        )
    ),
    ('Tutor', (
         'root_path',
         'user_path',
         'media_path',
         'user_media_path',
        )
    ),
]

class SettingsError(ValueError):
    pass

def settings_structure_doc():
    'Create docstring describing SETTINGS_STRUCTURE'

    examples = itertools.cycle([ 'ham', 'spam', 'eggs', 'foo', 'bar', 'foobar'])
    lines = []
    for section in SETTINGS_STRUCTURE:
        name, keys = section
        lines.append('\n[ %s ]' % name)
        for key, value in zip(keys, examples):
            lines.append('%s: %s' % (key, value))
    return '\n'.join(lines)

def read_all_conf_files():
    '''
    Read all configuration files and return the settings dictionary.
    The maximum structure of a configuration file is
    ----------------------------------------------------------------------------
    %(SETTINGS_STRUCTURE)s
    '''

    file_locations = ['/etc/tutor.conf', os.path.expanduser('~/.config/tutor.conf')]

    # Create config dict
    config = ConfigParser.SafeConfigParser()
    config.read(file_locations)
    config = dict((section, dict(config.items(section))) for section in config.sections())

    # Check if config dictionary is valid
    settings = dict(SETTINGS_STRUCTURE)
    for section, keys in config.items():
        if not section in settings:
            raise SettingsError("invalid section in configuration file, '%s'" % section)

        valid_keys = set(settings[section])
        for key in keys:
            if key not in valid_keys:
                raise SettingsError("invalid key '%s' in section '%s' of configuration file" % (key, section))

    return config

read_all_conf_files.func_doc = read_all_conf_files.func_doc % \
    {'SETTINGS_STRUCTURE': '\n'.join('    ' + l for l in settings_structure_doc().splitlines())}

def settings():
    '''
    Make the settings dictionary from configuration files and append versioning
    information 
    '''

    settings = read_all_conf_files()
    settings['Version'] = VERSION
    return settings

SETTINGS = settings()
SETTINGS['Tutor'] = {}
SETTINGS['Tutor']['root_path'] = '/var/lib/tutor/'
SETTINGS['Tutor']['user_path'] = os.path.expanduser('~/.local/lib/tutor/')

if __name__ == '__main__':
    print('Settings file')
    print('-' * 80)
    print(settings_structure_doc())
    print()
    print('Settings')
    print('-' * 80)
    for k, v in SETTINGS.items():
        print('\n[%s]' % k)
        for k, v in v.items():
            print('%s: %s' % (k, v))
