from django import template
from incident import choices


register = template.Library()


@register.simple_tag
def get_case_status_display(case_status):
    return choices.LegalCaseStatus[case_status].label
