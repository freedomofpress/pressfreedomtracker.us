from django.utils.cache import patch_cache_control
from wagtail.wagtailcore.models import Page

from common.utils import DEFAULT_PAGE_KEY, paginate
from incident.models.incident_page import IncidentPage


class IncidentIndexPage(Page):
    content_panels = Page.content_panels

    subpage_types = ['incident.IncidentPage']

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
