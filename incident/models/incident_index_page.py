import csv
import json
from typing import TYPE_CHECKING

from django.db import models
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.utils.cache import patch_cache_control
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core.models import Page, Site
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from common.utils import DEFAULT_PAGE_KEY, paginate, Echo
from common.models import MetadataPageMixin
from common.models.settings import SearchSettings
from incident.models.export import to_row, is_exportable, to_json
from incident.models.incident_page import IncidentPage
from incident.utils.incident_filter import IncidentFilter, get_serialized_filters
from incident.feeds import IncidentIndexPageFeed

if TYPE_CHECKING:
    from django.http import HttpRequest  # noqa: F401


class IncidentIndexPage(RoutablePageMixin, MetadataPageMixin, Page):

    feed_limit = models.PositiveIntegerField(
        default=1000,
        help_text='Maximum number of incidents to be included in the '
                  'syndication feed. 0 for unlimited.'
    )

    content_panels = Page.content_panels
    settings_panels = Page.settings_panels + [
        FieldPanel('feed_limit')
    ]

    subpage_types = ['incident.IncidentPage']

    LIVEPREVIEW_DISABLED = True

    @route('export/')
    @method_decorator(require_http_methods(['HEAD', 'GET', 'OPTIONS']))
    def export_view(self, request: 'HttpRequest') -> HttpResponse:
        if request.method == 'GET':
            response = self.export_view_GET(request)
        else:  # Method is HEAD or OPTIONS
            response = self.export_view_OPTIONS(request)

        # Allow requests from any orign to allow this to be an accessible API
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET,OPTIONS,HEAD'

        return response

    def export_view_GET(self, request: 'HttpRequest') -> HttpResponse:
        export_format = request.GET.get('format', 'csv')
        allowed_fields = request.GET.get('fields')
        if not allowed_fields:
            allowed_fields = []
        else:
            allowed_fields = allowed_fields.split(',')
        incident_filter = IncidentFilter(request.GET)
        incidents = incident_filter.get_queryset()
        if export_format == 'json':
            return self.export_format_json(incidents, allowed_fields)
        else:
            return self.export_format_csv(incidents, allowed_fields)

    def export_format_csv(self, incidents, allowed_fields):
        if allowed_fields:
            incident_fields = [f for f in IncidentPage._meta.get_fields() if f.name in allowed_fields]
        else:
            incident_fields = IncidentPage._meta.get_fields()
        headers = [field.name for field in incident_fields
                   if is_exportable(field)]

        # Helper function to combine data with headers
        def stream(headers, data):
            if headers:
                yield headers
            for incident in data:
                yield to_row(incident, allowed_fields)

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in stream(headers, incidents)),
            content_type="text/csv")

        response['Content-Disposition'] = 'attachment; filename="incidents.csv"'
        return response

    def export_format_json(self, incidents, fields):
        incident_list = []
        for incident in incidents:
            incident_list.append(to_json(incident, fields))
        return JsonResponse(
            incident_list,
            safe=False
        )

    def export_view_OPTIONS(self, request: 'HttpRequest') -> HttpResponse:
        return HttpResponse()

    @route(r'^feed/$')
    def feed(self, request):
        return IncidentIndexPageFeed(self)(request)

    def get_incidents(self):
        """Returns all published incident pages"""
        return IncidentPage.objects.live().order_by(
            # Incidents should be in reverse-chronological order by the
            # incident date, not when they were published.
            '-date',
            'path',
        )

    def get_context(self, request, *args, **kwargs):
        from common.models import CategoryPage
        context = super(IncidentIndexPage, self).get_context(request, *args, **kwargs)

        incident_filter = IncidentFilter(request.GET)
        context['serialized_filters'] = json.dumps(get_serialized_filters())

        search_settings = SearchSettings.for_site(Site.find_for_request(request))
        if search_settings.data_download_page:
            context['export_path'] = search_settings.data_download_page.get_url()
        else:
            context['export_path'] = self.url + self.reverse_subpage('export_view')

        incident_filter.clean()
        category_ids = incident_filter.cleaned_data.get('categories')

        if not category_ids:
            context['categories'] = CategoryPage.objects.live()
        else:
            context['categories'] = CategoryPage.objects.filter(live=True, pk__in=category_ids)

        incident_qs = incident_filter.get_queryset()

        paginator, entries = paginate(
            request,
            incident_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=8,
            orphans=5
        )

        context['entries_page'] = entries
        context['paginator'] = paginator
        context['summary_table'] = incident_filter.get_summary()

        if request.is_ajax():
            context['layout_template'] = 'base.ajax.html'
        else:
            context['layout_template'] = 'base.html'

        return context

    def get_cache_tag(self):
        return 'incident-index-{}'.format(self.pk)

    def serve(self, request, *args, **kwargs):
        response = super(IncidentIndexPage, self).serve(request, *args, **kwargs)

        # We set a cache tag here so that elsewhere we can purge all subroutes
        # of the incident index page (including paginated and filtered URLs)
        # simultaneously
        response['Cache-Tag'] = self.get_cache_tag()

        if request.is_ajax():
            # We don't want the browser to cache the response to an XHR because
            # it gets served with a different layout template. This becomes
            # problematic when a visitor hits the Back button in her browser
            # and ends up seeing the cached version without any typical layout.
            #
            # n.b. This method mutates the response and returns None.
            patch_cache_control(
                response,
                no_cache=True,
                no_store=True,
                must_revalidate=True,
            )
        return response
