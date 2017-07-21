from django.conf.urls import url
from wagtail.wagtailadmin.decorators import require_admin_access

from autocomplete.views import objects, search, create


urlpatterns = [
    url(r'^objects/', objects),
    url(r'^search/', search),
]
