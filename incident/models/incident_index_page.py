import csv

from django.db import models
from django.http import StreamingHttpResponse
from django.utils.cache import patch_cache_control
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route

from common.models.pages import CategoryPage
from common.utils import DEFAULT_PAGE_KEY, paginate, Echo
from common.models import MetadataPageMixin
from incident.models.choices import get_filter_choices
from incident.models.export import to_row, is_exportable
from incident.models.incident_page import IncidentPage
from incident.utils.incident_filter import IncidentFilter
from incident.feeds import IncidentIndexPageFeed


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

    @route('export/')
    def export_view(self, request):
        incident_filter = IncidentFilter(request.GET)
        incidents = incident_filter.get_queryset()

        incident_fields = IncidentPage._meta.get_fields()
        headers = [field.name for field in incident_fields
                   if is_exportable(field)]

        # Helper function to combine data with headers
        def stream(headers, data):
            if headers:
                yield headers
            for incident in data:
                yield to_row(incident)

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse(
            (writer.writerow(row) for row in stream(headers, incidents)),
            content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="incidents.csv"'
        return response

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

    def get_context(self, request):
        context = super(IncidentIndexPage, self).get_context(request)

        incident_filter = IncidentFilter(request.GET)
        context['category_options'] = incident_filter.get_category_options()
        context['filter_choices'] = get_filter_choices()
        context['export_path'] = self.url

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
