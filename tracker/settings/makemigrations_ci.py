from .dev import *

DATABASES = {
    'default' : {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'ci',
        'USER': 'ci_user',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
}
