from django.conf.urls import url
from .views import search, create


urlpatterns = [
    url(r'^search/', search),
    url(r'^create/', create),
]
