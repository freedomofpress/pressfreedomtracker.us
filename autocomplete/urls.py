from django.conf.urls import url
from .views import objects, search, create


urlpatterns = [
    url(r'^objects/', objects),
    url(r'^search/', search),
    url(r'^create/', create),
]
