from __future__ import absolute_import, unicode_literals

import os
import socket
import struct
from .base import *  # noqa: F403, F401


if not os.environ.get('DJANGO_DISABLE_DEBUG'):
    DEBUG = True


# The example SECRET_KEY below is used only in the local dev env.
# In the production settings file, a custom env var is required
# to run the application.
SECRET_KEY = '(g4bj*$%zf4tqdaas8#ch3-mz_27n+*-973tpxap9zmdz8ii_u'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *  # noqa: F403, F401
except ImportError:
    pass


def get_default_gateway_linux():
    """
       Read the default gateway directly from /proc. Doesnt require subprocess
       or an external python dep.
       Ref: https://stackoverflow.com/questions/2761829/python-get-default-gateway-for-a-local-interface-ip-address-in-linux
    """
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))


if DEBUG:
    if os.environ.get('DJANGO_PROFILE', 'no').lower() == 'yes':
        # Silk
        INSTALLED_APPS.append('silk')
        MIDDLEWARE = ['silk.middleware.SilkyMiddleware'] + MIDDLEWARE

        # Django CProfile Middleware
        MIDDLEWARE.append('django_cprofile_middleware.middleware.ProfilerMiddleware')
        DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF = False


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

    # Disable caching of webpack stats files (can prevent node/django
    # container race condition).
    WEBPACK_LOADER['DEFAULT']['CACHE'] = False  # noqa: F405

    # Obtain the default gateway from docker, needed for
    # debug toolbar whitelisting
    INTERNAL_IPS = [get_default_gateway_linux()]
    INSTALLED_APPS.append('debug_toolbar')  # noqa: F405
    # Needs to be injected relatively early in the MIDDLEWARE list
    MIDDLEWARE.insert(4, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405
    # Include the wagtail styleguide
    INSTALLED_APPS.append('wagtail.contrib.styleguide')  # noqa: F405


if 'DJANGO_NO_DB' in os.environ:
    pass
else:
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

# Prevent endless waiting if problem loading webpack bundles.
WEBPACK_LOADER['DEFAULT']['TIMEOUT'] = 60  # noqa: F405
