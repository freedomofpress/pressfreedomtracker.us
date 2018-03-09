from __future__ import absolute_import, unicode_literals

import os
import subprocess
from django.conf import settings
from .base import *  # noqa: F403, F401

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(g4bj*$%zf4tqdaas8#ch3-mz_27n+*-973tpxap9zmdz8ii_u'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *  # noqa: F403, F401
except ImportError:
    pass

if settings.DEBUG:
    # Fix for https://github.com/jazzband/django-debug-toolbar/issues/950
    DEBUG_TOOLBAR_CONFIG = {
        'SKIP_TEMPLATE_PREFIXES': (
            'django/forms/widgets/',
            'admin/widgets/',
            'common/blocks/',
            'statistics/'
        ),
        'DISABLE_PANELS': {
            'debug_toolbar.panels.redirects.RedirectsPanel',
            'debug_toolbar.panels.redirects.TemplatesPanel'
        },
    }

    # Obtain the default gateway from docker, needed for
    # debug toolbar whitelisting
    docker_gw = subprocess.check_output('ip r | head -n 1', shell=True)
    INSTALLED_APPS.append('debug_toolbar')  # noqa: F405
    # Needs to be injected relatively early in the MIDDLEWARE list
    MIDDLEWARE.insert(4, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405
    INTERNAL_IPS = [docker_gw.split()[2].decode("utf-8")]
    # Include the wagtail styleguide
    INSTALLED_APPS.append('wagtail.contrib.wagtailstyleguide')  # noqa: F405

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DJANGO_DB_NAME'],
        'USER': os.environ['DJANGO_DB_USER'],
        'PASSWORD': os.environ['DJANGO_DB_PASSWORD'],
        'HOST': os.environ['DJANGO_DB_HOST'],
        'PORT': os.environ['DJANGO_DB_PORT'],
        'CONN_MAX_AGE': os.environ.get('DJANGO_DB_MAX_AGE', 600)
    }
}
