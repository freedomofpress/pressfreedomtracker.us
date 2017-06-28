from django import template
from django.template import Template, Variable, TemplateSyntaxError


register = template.Library()


class RenderAsTemplateNode(template.Node):
    def __init__(self, item_to_be_rendered):
        self.item_to_be_rendered = Variable(item_to_be_rendered)

    def render(self, context):
        try:
            actual_item = self.item_to_be_rendered.resolve(context)
            return Template(actual_item).render(context)
        except template.VariableDoesNotExist:
            return ''


@register.tag
def render_as_template(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError(
            "'%s' takes only one argument"
            " (a variable representing a template to render)" % bits[0])
    return RenderAsTemplateNode(bits[1])
