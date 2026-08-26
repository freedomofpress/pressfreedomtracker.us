from django import template
from django.template import Context, Template


register = template.Library()


@register.simple_tag
def render_as_template(template_content):
    return Template(template_content).render(Context())
