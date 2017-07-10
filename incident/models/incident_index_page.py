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

        incident_filter = IncidentFilter(
            search_text=request.GET.get('search'),
            lower_date=request.GET.get('lower_date'),
            upper_date=request.GET.get('upper_date'),
            categories=request.GET.get('categories'),
            targets=request.GET.get('targets'),
            affiliation=request.GET.get('affiliation'),
            states=request.GET.get('states'),
            tags=request.GET.get('tags'),
            # ARREST / DETENTION
            arrest_status=request.GET.get('arrest_status'),
            status_of_charges=request.GET.get('status_of_charges'),
            current_charges=request.GET.get('current_charges'),
            dropped_charges=request.GET.get('dropped_charges'),
            # EQUIPMENT
            equipment_seized=request.GET.get('equipment_seized'),
            equipment_broken=request.GET.get('equipment_broken'),
            status_of_seized_equipment=request.GET.get('status_of_seized_equipment'),
            is_search_warrant_obtained=request.GET.get('is_search_warrant_obtained'),
            actor=request.GET.get('actors'),
            # BORDER STOP
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
            # PHYSICAL ASSAULT
            assailant=request.GET.get('assailant'),
            was_journalist_targeted=request.GET.get('was_journalist_targeted'),
            # LEAK PROSECUTION
            charged_under_espionage_act=request.GET.get('charged_under_espionage_act'),
            # SUBPOENA
            subpoena_subject=request.GET.get('subpoena_subject'),
            subpoena_type=request.GET.get('subpoena_type'),
            subpoena_status=request.GET.get('subpoena_status'),
            held_in_contempt=request.GET.get('held_in_contempt'),
            detention_status=request.GET.get('detention_status'),
            third_party_in_possession_of_communications=request.GET.get('third_party_in_possession_of_communications'),
            third_party_business=request.GET.get('third_party_business'),
            legal_order_type=request.GET.get('legal_order_type'),
            # PRIOR RESTRAINT
            status_of_prior_restraint=request.GET.get('status_of_prior_restraint'),
            # DENIAL OF ACCESS
            politicians_or_public_figures_involved=request.GET.get('politicians_or_public_figures_involved'),
        )
        context['category_options'] = incident_filter.get_category_options()
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
