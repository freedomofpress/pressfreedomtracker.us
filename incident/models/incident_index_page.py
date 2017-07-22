import csv

from django.http import StreamingHttpResponse
from django.utils.cache import patch_cache_control
from wagtail.wagtailcore.models import Page
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route

from common.utils import DEFAULT_PAGE_KEY, paginate, Echo
from incident.models.choices import get_filter_choices
from incident.models.export import to_row, is_exportable
from incident.models.incident_page import IncidentPage
from incident.utils.incident_filter import IncidentFilter


class IncidentIndexPage(RoutablePageMixin, Page):
    content_panels = Page.content_panels

    subpage_types = ['incident.IncidentPage']

    @route('export/')
    def export_view(self, request):
        incidents = self.get_incidents()
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
        response['Content-Disposition'] = 'attachment; filename="all_incidents.csv"'
        return response

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

        incident_filter = IncidentFilter.from_request(request)
        context['category_options'] = incident_filter.get_category_options()
        context['filter_choices'] = get_filter_choices()
        entry_qs = incident_filter.fetch()

        paginator, entries = paginate(
            request,
            entry_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=8,
            orphans=5
        )

        context['entries_page'] = entries
        context['paginator'] = paginator

        if request.is_ajax():
            context['layout_template'] = 'base.ajax.html'
        else:
            context['layout_template'] = 'base.html'

        return context

    def serve(self, request, *args, **kwargs):
        response = super(IncidentIndexPage, self).serve(request, *args, **kwargs)
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
