from django.urls import path

from .views import StyleguideView


urlpatterns = [
    path("", StyleguideView.as_view(), name="styleguide"),
]
