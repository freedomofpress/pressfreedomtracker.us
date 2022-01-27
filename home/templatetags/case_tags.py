from django import template
from incident.models import choices


register = template.Library()


@register.simple_tag
def get_case_status_display(case_status):
    return dict(choices.CASE_STATUS).get(case_status)
