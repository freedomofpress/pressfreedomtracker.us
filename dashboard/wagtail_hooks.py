from wagtail import hooks
from wagtail.admin.ui.components import Component

from incident.models import PrepublicationIncidentSync


class ShortcutsPanel(Component):
    # This is an ordering number that is the minimum multiple of 10 to place
    # this panel underneath the built-in Wagtail panels.
    order = 100
    template_name = "dashboard/shortcuts_panel.html"

    def get_context_data(self, parent_context):
        context = super().get_context_data(parent_context)
        prepub_sync = PrepublicationIncidentSync.objects.prefetch_related(
            "skipped_rows"
        ).first()
        if prepub_sync:
            context["prepub_sync"] = prepub_sync
            if len(prepub_sync.skipped_rows.all()) > 0:
                context["prepub_sync_extended_message"] = True
            else:
                context["prepub_sync_extended_message"] = False
        return context


@hooks.register("construct_homepage_panels")
def add_shortcuts_panel(request, panels):
    return panels.append(ShortcutsPanel())
