from wagtail import hooks
from wagtail.admin.ui.components import Component


class ShortcutsPanel(Component):
    # This is an ordering number that is the minimum multiple of 10 to place
    # this panel underneath the built-in Wagtail panels.
    order = 100
    template_name = 'dashboard/shortcuts_panel.html'


@hooks.register('construct_homepage_panels')
def add_shortcuts_panel(request, panels):
    return panels.append(ShortcutsPanel())
