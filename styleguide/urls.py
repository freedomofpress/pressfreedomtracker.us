from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from .views import StyleguideView


urlpatterns = [
    re_path(r'$', StyleguideView.as_view(), name='styleguide'),
]
