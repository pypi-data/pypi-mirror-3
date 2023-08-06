#-*- coding: utf-8 -*-
DJANGO_STARTED = False

def start_django():
    """Startup Django ORM."""

    global DJANGO_STARTED

    if not DJANGO_STARTED:
        from tutor.db import settings
        from django.core.management import setup_environ
        setup_environ(settings, 'tutor.db.settings')

    DJANGO_STARTED = True

if not DJANGO_STARTED:
    start_django()
