from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from wagtail.wagtailadmin.edit_handlers import EditHandler


class BaseHelpPanel(EditHandler):
    template = "common/edit_handlers/help_panel.html"

    def classes(self):
        classes = super(BaseHelpPanel, self).classes()
        return classes + [
            "full",
            "title",
        ]

    def render(self, *args, **kwargs):
        return mark_safe(render_to_string(self.template, dict(self=self)))  # nosec


class HelpPanel(object):
    def __init__(self, text, *args, **kwargs):
        self.text = text

    def bind_to_model(self, *args, **kwargs):
        return type(str('_HelpPanel'), (BaseHelpPanel,), {
            'text': self.text,
        })
