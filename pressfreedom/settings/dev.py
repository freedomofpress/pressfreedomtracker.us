from __future__ import absolute_import, unicode_literals


from .base import *  # noqa: F403, F401

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(g4bj*$%zf4tqdaas8#ch3-mz_27n+*-973tpxap9zmdz8ii_u'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *  # noqa: F403, F401
except ImportError:
    pass
