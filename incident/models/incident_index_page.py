from wagtail.wagtailcore.models import Page

from common.utils import DEFAULT_PAGE_KEY, paginate
from incident.models.incident_page import IncidentPage


class IncidentIndexPage(Page):
    content_panels = Page.content_panels

    subpage_types = ['incident.IncidentPage']

    def get_incidents(self):
        """Returns all published incident pages"""
        return IncidentPage.objects.live()

    def get_context(self, request):
        context = super(IncidentIndexPage, self).get_context(request)

        entry_qs = self.get_incidents()

        paginator, entries = paginate(
            request,
            entry_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=8,
            orphans=5
        )

        context['entries_page'] = entries
        context['paginator'] = paginator

        return context
