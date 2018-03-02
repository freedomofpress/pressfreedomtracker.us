from django import template
from django.template import Template, Context


register = template.Library()


@register.simple_tag
def render_as_template(template_content):
    return Template(template_content).render(Context())
