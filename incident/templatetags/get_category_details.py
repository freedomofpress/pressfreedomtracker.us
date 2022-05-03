from django import template


register = template.Library()


@register.simple_tag
def get_category_details(incident, index):
    return incident.get_category_details(index)
