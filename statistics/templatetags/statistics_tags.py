from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth

from incident.models.incident_page import IncidentPage
from statistics.registry import statistic, get_stats


register = template.Library()


@statistic
@register.simple_tag
def num_incidents(year):
    """Return the count of incidents occurring in the given year"""
    return IncidentPage.objects.filter(
        live=True,
        date__year=year,
    ).count()


@statistic
@register.simple_tag
def incidents_in_year_range_by_month(start_year, end_year):
    """Return a list of (Month, Count) pairs for incidents within timespan

    Indended to be consumed and rendered by some form of visualization
    template.

    """
    data = (
        IncidentPage.objects
        .filter(
            live=True,
            date__year__gte=start_year,
            date__year__lte=end_year,
        )
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(c=Count('*')).order_by('month')
    )
    return [(i['month'].strftime('%B %Y'), i['c']) for i in data]


@register.simple_tag
def display_stat(statistic, params):
    """Not totally sure this is needed."""
    stats = get_stats()
    return stats[statistic](*params.split())
