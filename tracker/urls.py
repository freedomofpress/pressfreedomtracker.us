from __future__ import absolute_import, unicode_literals

from django.apps import apps
from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls
from wagtailautocomplete.views import objects, search

from common import views as common_views
from emails import urls as emails_urls
from incident.api.urls import api_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls


autocomplete_public_urls = [
    path('objects/', objects),
    path('search/', search),
]

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('api/edge/', include(api_urls)),
    path('autocomplete/', include(autocomplete_public_urls)),
    path('admin/autocomplete/', include(autocomplete_admin_urls)),
    path('admin/', include(wagtailadmin_urls)),
    path('emails/', include(emails_urls)),

    re_path(r'^documents/(\d+)/(.*)$', common_views.serve),
    path('documents/', include(wagtaildocs_urls)),

    path('health/ok/', common_views.health_ok),
    path('health/version/', common_views.health_version),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns


if settings.ENABLE_DEBUG_TOOLBAR:
    urlpatterns.append(path('__debug__/', include('debug_toolbar.urls')))


if settings.STYLEGUIDE:
    urlpatterns = [path('styleguide/', include('styleguide.urls'))] + urlpatterns

if apps.is_installed('silk'):
    urlpatterns = [path('silk/', include('silk.urls', namespace='silk'))] + urlpatterns

urlpatterns.append(path(r'', include(wagtail_urls)))
