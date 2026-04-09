from __future__ import absolute_import, unicode_literals

from django.urls import path

from .views import StyleguideView


urlpatterns = [
    path("", StyleguideView.as_view(), name="styleguide"),
]
