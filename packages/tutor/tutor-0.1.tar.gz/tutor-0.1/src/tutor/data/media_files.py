import os
from tutor import SETTINGS

TUTOR = SETTINGS['Tutor']
TUTOR_ROOT = TUTOR['root_path']
TUTOR_USER = TUTOR['user_path']
MEDIA_ROOT = TUTOR.setdefault('media_path', os.path.join(TUTOR_ROOT, 'media'))
MEDIA_USER = TUTOR.setdefault('user_media_path', os.path.join(TUTOR_USER, 'media'))

# Update MEDIA_FILES
MEDIA_FILES = {}
if os.path.exists(MEDIA_ROOT):
    for f in os.listdir(MEDIA_ROOT):
        MEDIA_FILES[f] = os.path.join(MEDIA_ROOT, f)
if os.path.exists(MEDIA_USER):
    for f in os.listdir(MEDIA_USER):
        MEDIA_FILES[f] = os.path.join(MEDIA_USER, f)
