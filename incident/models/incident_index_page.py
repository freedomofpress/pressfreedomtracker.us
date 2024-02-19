import csv
import json
import copy
from typing import TYPE_CHECKING

from django.db import models
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.utils.cache import patch_cache_control
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from marshmallow import Schema, fields, EXCLUDE
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page, Site
from wagtail.contrib.routable_page.models import RoutablePageMixin, path

from common.utils import DEFAULT_PAGE_KEY, paginate, Echo
from common.models import MetadataPageMixin
from common.models.settings import SearchSettings
from incident.models.export import to_row, is_exportable, to_json
from incident.models.incident_page import IncidentPage
from incident.utils.forms import get_filter_forms
from incident.utils.incident_filter import IncidentFilter, ManyRelationValue, get_serialized_filters
from incident.feeds import IncidentIndexPageFeed

if TYPE_CHECKING:
    from django.http import HttpRequest  # noqa: F401


class SummarySchema(Schema):
    class Meta:
        # This schema is populated from the incident filter results
        # summary, which can contain dynamic fields.  EXCLUDE tells
        # the schema to ignore those.
        unknown = EXCLUDE
    total = fields.Integer(data_key='Total Results')
    journalists = fields.Integer(data_key='Journalists affected')
    institutions = fields.Integer(data_key='Institutions affected')


class IncidentIndexPage(RoutablePageMixin, MetadataPageMixin, Page):

    feed_limit = models.PositiveIntegerField(
        default=1000,
        help_text='Maximum number of incidents to be included in the '
                  'syndication feed. 0 for unlimited.'
    )
    feed_per_page = models.PositiveIntegerField(
        default=20,
        help_text='Maximum number of incidents to be included per page '
                  'in the syndication feed.'
    )

    content_panels = Page.content_panels
    settings_panels = Page.settings_panels + [
        FieldPanel('feed_limit'),
        FieldPanel('feed_per_page'),
    ]

    subpage_types = ['incident.IncidentPage']

    @path('export/')
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
        incidents = incident_filter.get_queryset() \
            .select_related('teaser_image', 'state', 'arresting_authority') \
            .prefetch_related(
                'authors',
                'categories__category',
                'current_charges',
                'dropped_charges',
                'equipment_broken__equipment',
                'equipment_seized__equipment',
                'links',
                'politicians_or_public_figures_involved',
                'tags',
                'target_nationality',
                'targeted_institutions',
                'targeted_journalists',
                'teaser_image__renditions',
                'updates',
                'venue',
                'workers_whose_communications_were_obtained',
        )
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

    @path('summary/')
    @method_decorator(require_http_methods(['GET']))
    def summary(self, request):
        incident_filter = IncidentFilter(request.GET)
        summary = incident_filter.get_summary()
        result = SummarySchema().load(dict(summary))
        return JsonResponse(result)

    @path('feed/')
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
        context = super(IncidentIndexPage, self).get_context(request, *args, **kwargs)

        # Before perf change:
        # context['all_incident_count'] = len(IncidentFilter({}).get_queryset())

        # Quickest:
        context['all_incident_count'] = IncidentPage.objects.live().count()

        # Could also be:
        # context['all_incident_count'] = IncidentFilter({}).get_queryset().count()

        incident_filter = IncidentFilter(request.GET)
        context['serialized_filters'] = json.dumps(get_serialized_filters())

        search_settings = SearchSettings.for_site(Site.find_for_request(request))
        if search_settings.data_download_page:
            context['export_path'] = search_settings.data_download_page.get_url()
        else:
            context['export_path'] = self.url + self.reverse_subpage('export_view')

        if search_settings.learn_more_page:
            context['learn_more_path'] = search_settings.learn_more_page.get_url()

        incident_filter.clean()
        context['search_value'] = incident_filter.cleaned_data.get('search', '')

        if incident_filter.cleaned_data:
            export_filter_data = copy.deepcopy(incident_filter.cleaned_data)
            for name, value in export_filter_data.items():
                if isinstance(value, ManyRelationValue):
                    filter_values = [str(i) for i in value.pks] + value.strings
                    export_filter_data[name] = ",".join(filter_values)

            context['filtered_export_path'] = (
                context['export_path'] +
                '?' +
                incident_filter.get_url_parameters()
            )

        incident_qs = incident_filter.get_queryset() \
            .with_public_associations() \
            .with_most_recent_update() \

        paginator, entries = paginate(
            request,
            incident_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=8,
            orphans=5
        )

        context['entries_page'] = entries
        context['paginator'] = paginator

        get_data = request.GET.copy()
        context['sort_choices'] = []
        for value, label in IncidentFilter.SortOptions.choices:
            get_data['sort'] = value
            context['sort_choices'].append(
                (get_data.urlencode(), label, value == incident_filter.sort.value)
            )
        context['selected_sort'] = incident_filter.sort

        # Before perf change:
        # context['incident_count'] = len(incident_qs)

        # Quickest:
        context['incident_count'] = paginator.count

        # Could also be:
        # context['incident_count'] = incident_qs.count()

        context['filters'] = get_filter_forms(request, json.loads(context['serialized_filters']))

        return context

    def get_cache_tag(self):
        return 'incident-index-{}'.format(self.pk)

    def serve(self, request, *args, **kwargs):
        response = super(IncidentIndexPage, self).serve(request, *args, **kwargs)

        # We set a cache tag here so that elsewhere we can purge all subroutes
        # of the incident index page (including paginated and filtered URLs)
        # simultaneously
        response['Cache-Tag'] = self.get_cache_tag()
        return response
