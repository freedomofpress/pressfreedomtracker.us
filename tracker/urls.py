from __future__ import absolute_import, unicode_literals

from django.apps import apps
from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls

from charts.urls import urlpatterns as chart_urls
from common import views as common_views
from emails import urls as emails_urls
from incident.api.urls import urlpatterns as api_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls


urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('admin/autocomplete/', include(autocomplete_admin_urls)),
    path('admin/', include(wagtailadmin_urls)),
    path('emails/', include(emails_urls)),

    re_path(r'^documents/(\d+)/(.*)$', common_views.serve),
    path('documents/', include(wagtaildocs_urls)),

    path('health/ok/', common_views.health_ok),
    path('health/version/', common_views.health_version),
    path('csrf/', common_views.get_csrf_token, name='csrf_token'),
    path('sitemap.xml', sitemap),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path(
        'subscribe_for_site/',
        common_views.SubscribeForSite.as_view(),
        name='subscribe_for_site',
    ),

    path('charts/', include(chart_urls)),

    path('api/schema/', SpectacularAPIView.as_view(api_version='edge'), name='schema'),
    # Schema UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path(r'', include(api_urls)),
    path(r'', include(wagtail_urls)),
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
