from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth

from incident.models.incident_page import IncidentPage


register = template.Library()


@register.simple_tag
def num_incidents(year):
    """Return the count of incidents occurring in the given year"""
    return IncidentPage.objects.filter(
        live=True,
        date__year=year,
    ).count()


@register.simple_tag
def incidents_in_year_range_by_month(start_year, end_year):
    data = (
        IncidentPage.objects
        .filter(
            date__year__gte=start_year,
            date__year__lte=end_year,
        )
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(c=Count('*')).order_by()
    )
    return { i['month'].strftime('%B %Y'): i['c'] for i in data }


def as_table():
    pass

def as_histogram():
    pass

def as_statbox():
    pass
