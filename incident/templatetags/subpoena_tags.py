from django import template
from incident import choices


register = template.Library()


@register.simple_tag
def get_subpoena_status_display(subpoena_status):
    return dict(choices.SUBPOENA_STATUS).get(subpoena_status)
