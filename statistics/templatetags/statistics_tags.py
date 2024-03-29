from django import template
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.db.models.functions import TruncMonth

from common.validators import tag_validator
from statistics.registry import Statistics
from statistics.utils import parse_kwargs


register = template.Library()
statistics = Statistics()


@statistics.number
@register.simple_tag
def num_incidents(**kwargs):
    """Return the count of incidents matching the given filter parameters"""
    from incident.utils.incident_filter import IncidentFilter

    incident_filter = IncidentFilter(kwargs)
    try:
        incident_filter.clean(strict=True)
    except ValidationError:
        # Don't return an incorrect number if params are invalid.
        return ''
    return incident_filter.get_queryset().count()


@statistics.number
@register.simple_tag
def num_institution_targets(**kwargs):
    from incident.models.items import Institution
    from incident.utils.incident_filter import IncidentFilter

    incident_filter = IncidentFilter(kwargs)
    try:
        incident_filter.clean(strict=True)
    except ValidationError:
        return ''
    queryset = incident_filter.get_queryset()
    return Institution.objects.filter(institutions_incidents__in=queryset).distinct().count()


@statistics.number
@register.simple_tag
def num_journalist_targets(**kwargs):
    from incident.models.items import Journalist, TargetedJournalist
    from incident.utils.incident_filter import IncidentFilter

    incident_filter = IncidentFilter(kwargs)
    try:
        incident_filter.clean(strict=True)
    except ValidationError:
        return ''
    queryset = incident_filter.get_queryset()
    tj_queryset = TargetedJournalist.objects.filter(incident__in=queryset)
    return Journalist.objects.filter(
        targeted_incidents__in=tj_queryset,
    ).distinct().count()


@statistics.number
@register.simple_tag
def num_targets(**kwargs):
    """Return the total count of journalist and institution targets


    Using the given filter parameters, sum the number of journalist
    and institution targets for matching incidents.

    """
    from incident.models.items import Journalist, TargetedJournalist, Institution
    from incident.utils.incident_filter import IncidentFilter

    incident_filter = IncidentFilter(kwargs)
    try:
        incident_filter.clean(strict=True)
    except ValidationError:
        # Don't return an incorrect number if params are invalid.
        return ''
    queryset = incident_filter.get_queryset()

    journalist_queryset = TargetedJournalist.objects.filter(incident__in=queryset)
    journalist_count = Journalist.objects.filter(
        targeted_incidents__in=journalist_queryset,
    ).distinct().count()

    institution_count = Institution.objects.filter(institutions_incidents__in=queryset).distinct().count()
    return journalist_count + institution_count


@tag_validator(register, 'num_targets')
@tag_validator(register, 'num_institution_targets')
@tag_validator(register, 'num_journalist_targets')
@tag_validator(register, 'num_incidents')
def validate_filter_kwargs(parser, token):
    """Return the count of incidents matching the given filter parameters"""
    from incident.utils.incident_filter import IncidentFilter

    bits = token.split_contents()
    tag_name, bits = bits[0], bits[1:]

    if len(bits) >= 2 and bits[-2] == 'as':
        bits = bits[:-2]

    try:
        kwargs = parse_kwargs(bits)
    except ValueError as exc:
        raise template.TemplateSyntaxError(
            '{}: {}'.format(tag_name, str(exc))
        )

    incident_filter = IncidentFilter(kwargs)
    incident_filter.clean(strict=True)


@statistics.map
@register.simple_tag
def incidents_in_year_range_by_month(start_year, end_year):
    """Return a list of (Month, Count) pairs for incidents within timespan

    Indended to be consumed and rendered by some form of visualization
    template.

    """
    from incident.models.incident_page import IncidentPage
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
