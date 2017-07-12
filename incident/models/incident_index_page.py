import csv

from django.http import StreamingHttpResponse
from django.utils.cache import patch_cache_control
from wagtail.wagtailcore.models import Page
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route

from common.utils import DEFAULT_PAGE_KEY, paginate, Echo
from incident.models.export import to_row, is_exportable
from incident.models.incident_page import IncidentPage
from incident.utils import IncidentFilter


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

        entry_qs = IncidentFilter(
            search_text=request.GET.get('search'),
            lower_date=request.GET.get('lower_date'),
            upper_date=request.GET.get('upper_date'),
            categories=request.GET.get('categories'),
            targets=request.GET.get('targets'),
            affiliation=request.GET.get('affiliation'),
            states=request.GET.get('states'),
            tags=request.GET.get('tags'),
            arrest_status=request.GET.get('arrest_status'),
            status_of_charges=request.GET.get('status_of_charges'),
            current_charges=request.GET.get('current_charges'),
            dropped_charges=request.GET.get('dropped_charges'),
            equipment_seized=request.GET.get('equipment_seized'),
            equipment_broken=request.GET.get('equipment_broken'),
            status_of_seized_equipment=request.GET.get('status_of_seized_equipment'),
            is_search_warrant_obtained=request.GET.get('is_search_warrant_obtained'),
            actors=request.GET.get('actors'),
            charged_under_espionage_act=request.GET.get('charged_under_espionage_act'),
            politicians_or_public_figures_involved=request.GET.get('politicians_or_public_figures_involved'),
            border_point=request.GET.get('border_point'),
            stopped_at_border=request.GET.get('stopped_at_border'),
            target_us_citizenship_status=request.GET.get('target_us_citizenship_status'),
            denial_of_entry=request.GET.get('denial_of_entry'),
            stopped_previously=request.GET.get('stopped_previously'),
            target_nationality=request.GET.get('target_nationality'),
            did_authorities_ask_for_device_access=request.GET.get('did_authorities_ask_for_device_access'),
            did_authorities_ask_for_social_media_user=request.GET.get('did_authorities_ask_for_social_media_user'),
            did_authorities_ask_for_social_media_pass=request.GET.get('did_authorities_ask_for_social_media_pass'),
            did_authorities_ask_about_work=request.GET.get('did_authorities_ask_about_work'),
            were_devices_searched_or_seized=request.GET.get('weredevices_searched_or_seized'),
        ).fetch()

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
