from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls
from wagtailautocomplete.views import objects, search

from common import views as common_views
from emails import urls as emails_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls


autocomplete_public_urls = [
    url(r'^objects/', objects),
    url(r'^search/', search),
]

urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls)),

    url(r'^autocomplete/', include(autocomplete_public_urls)),
    url(r'^admin/autocomplete/', include(autocomplete_admin_urls)),
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^emails/', include(emails_urls)),

    url(r'^documents/(\d+)/(.*)$', common_views.serve),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns

    # Debugtoolbar isnt always installed in prod, but sometimes i need to
    # toggle debug mode there.
    try:
        import debug_toolbar
        urlpatterns = [url(r'^styleguide/', include('styleguide.urls')),
                       url(r'^__debug__/', include(debug_toolbar.urls))
                       ] + urlpatterns
    except ImportError:
        pass
