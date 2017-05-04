from __future__ import absolute_import, unicode_literals

from .base import *  # noqa: F403, F401

DEBUG = False

try:
    from .local import *  # noqa: F403, F401
except ImportError:
    pass
