from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from wagtail.admin.edit_handlers import EditHandler


class HelpPanel(EditHandler):
    template = "common/edit_handlers/help_panel.html"

    def __init__(self, content='', heading='', classname=''):
        super().__init__(heading=heading, classname=classname)
        self.content = content

    def clone(self):
        return self.__class__(
            content=self.content,
            heading=self.heading,
            classname=self.classname,
        )

    def render(self):
        return mark_safe(render_to_string(self.template, {  # nosec
            'self': self
        }))
