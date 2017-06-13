from django import template

from incident.models.incident_page import IncidentPage


register = template.Library()


@register.simple_tag
def num_incidents(year):
    """Return the count of incidents occurring in the given year"""
    return IncidentPage.objects.filter(
        live=True,
        date__year=year,
    ).count()
