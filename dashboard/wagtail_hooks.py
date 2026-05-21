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
        prepub_sync = PrepublicationIncidentSync.objects.first()
        if prepub_sync:
            context["prepub_sync_completed_at"] = prepub_sync.completed_at
            context["prepub_sync_message"] = prepub_sync.message
            if prepub_sync.status == PrepublicationIncidentSync.Status.SUCCESS:
                context["prepub_sync_extended_message"] = False
            else:
                context["prepub_sync_extended_message"] = True
        return context


@hooks.register("construct_homepage_panels")
def add_shortcuts_panel(request, panels):
    return panels.append(ShortcutsPanel())
