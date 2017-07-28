from django import template
from django.db.models import Count
from django.db.models.functions import TruncMonth

from common.models.pages import CategoryPage
from incident.models.incident_page import IncidentPage
from incident.tests.test_filtering import create_incident_filter
from statistics.registry import Statistics


register = template.Library()
statistics = Statistics()


@statistics.number
@register.simple_tag
def num_by_category(category_name, lower_date=None, upper_date=None):
    """Count of all incidents in a particular category in an arbitrary
    date range

    Note: date arguments should be of the form 'YYYY-MM-DD'

    Keyword arguments:
    category_name -- the unique slug corresponding to a CategoryPage
    lower_date -- lower end of the date range (default None)
    upper_date -- upper end of the date range (default None)
    """
    category_page = CategoryPage.objects.get(slug=category_name)
    f = create_incident_filter(lower_date=lower_date, upper_date=upper_date,
                               category=category_page)
    _, incidents = f.fetch()
    return incidents.count()


@statistics.number
@register.simple_tag
def arrests_by_status(
        lower_date=None,
        upper_date=None,
        arrest_status=None,
        status_of_charges=None,
        detention_date_lower=None,
        detention_date_upper=None,
        release_date_lower=None,
        release_date_upper=None,
        unnecessary_use_of_force=None,
):
    """Count of arrests by various metrics

    Notes: date arguments should be of the form 'YYYY-MM-DD'

    Choice arguments must exactly match the case shown, and can be
    combined with commas, e.g. status_of_charges='CONVICTED,ACQUITTED'
    returns the count for both statuses.

    Keyword arguments:
    lower_date -- lower end of the incident date range (default None)
    upper_date -- upper end of the incident date range (default None)

    arrest_status -- choice of UNKNOWN, DETAINED_NO_PROCESSING,
    DETAINED_CUSTODY, ARRESTED_CUSTODY, ARRESTED_RELEASED.

    status_of_charges -- choice of UNKNOWN, NOT_CHARGED,
    CHARGES_PENDING, CHARGES_DROPPED, CONVICTED, ACQUITTED,
    PENDING_APPEAL

    detention_date_lower -- lower end of the detention date range (default None)
    detention_date_upper -- upper end of the detention date range (default None)
    release_date_lower -- lower end of the release date range (default None)
    release_date_upper -- upper end of the release date range (default None)
    unnecessary_use_of_force -- True/False if unecessary force was used (default both)

    """
    f = create_incident_filter(
        lower_date=lower_date,
        upper_date=upper_date,
        arrest_status=arrest_status,
        status_of_charges=status_of_charges,
        detention_date_lower=detention_date_lower,
        detention_date_upper=detention_date_upper,
        release_date_lower=release_date_lower,
        release_date_upper=release_date_upper,
        unnecessary_use_of_force=unnecessary_use_of_force,
    )
    _, incidents = f.fetch()
    return incidents.count()


@statistics.number
@register.simple_tag
def num_arrests(year=None, pending_charges=False, dropped_charges=False):
    """Count of all arrests

    Keyword arguments
    year -- a year in which the incident occurred (default: all years)
    pending_charges -- True/False, include only incidents with pending
    charges (default False)
    dropped_charges -- True/False, include only incidents with dropped
    charges (default False)

    """
    print('pend', pending_charges, type(pending_charges))
    print('year', year)
    incidents = IncidentPage.objects.filter(
        live=True,
        # This is merely one way of determining if an incident is of
        # type "arrest" and there may be other, more accurate ways.
        arrest_status__isnull=False,
    )
    if year:
        incidents = incidents.filter(date__year=year)
    if pending_charges:
        incidents = incidents.filter(
            status_of_charges='CHARGES_PENDING',
            current_charges__isnull=False,
        )
    if dropped_charges:
        incidents = incidents.filter(dropped_charges__isnull=False)
    return incidents.count()


@statistics.number
@register.simple_tag
def num_incidents(year):
    """Return the count of incidents occurring in the given year"""
    return IncidentPage.objects.filter(
        live=True,
        date__year=year,
    ).count()


@statistics.map
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
