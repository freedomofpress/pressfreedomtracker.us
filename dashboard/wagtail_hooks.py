from django.template.loader import render_to_string
from wagtail.wagtailcore import hooks
from wagtail.wagtailcore.models import Site


class ShortcutsPanel:
    order = 100

    def __init__(self, request):
        self.request = request

    def render(self):
        site = Site.find_for_request(self.request)
        return render_to_string('dashboard/shortcuts_panel.html', dict(
            incident_page=site.root_page.specific.incident_index_page,
        ))


@hooks.register('construct_homepage_panels')
def add_shortcuts_panel(request, panels):
    return panels.append(ShortcutsPanel(request))
