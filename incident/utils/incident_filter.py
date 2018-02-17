from datetime import date
from itertools import chain

from django.core.exceptions import ValidationError
from django.db.models import (
    CharField,
    Count,
    DateField,
    DurationField,
    F,
    ManyToManyField,
    Q,
    Value,
)
from django.db.models.functions import Trunc, Cast
from django.db.models.fields.related import ManyToOneRel
from psycopg2.extras import DateRange

from common.models import CategoryPage
from incident.models.incident_page import IncidentPage
from incident.circuits import STATES_BY_CIRCUIT

from incident.utils.db import MakeDateRange


CATEGORIES = {
    'Arrest / Criminal Charge': [
        'arrest_status',
        'status_of_charges',
        'detention_date',
        'release_date',
        'unnecessary_use_of_force',
    ],
    'Border Stop': [
        'border_point',
        'stopped_at_border',
        'stopped_previously',
        'target_us_citizenship_status',
        'denial_of_entry',
        'target_nationality',
        'did_authorities_ask_for_device_access',
        'did_authorities_ask_for_social_media_user',
        'did_authorities_ask_for_social_media_pass',
        'did_authorities_ask_about_work',
        'were_devices_searched_or_seized',
    ],
    'Denial of Access': [
        'politicians_or_public_figures_involved',
    ],
    'Equipment Search or Seizure': [
        'equipment_seized',
        'equipment_broken',
        'status_of_seized_equipment',
        'is_search_warrant_obtained',
        'actor',
    ],
    'Leak Case': [
        'charged_under_espionage_act',
    ],
    'Physical Attack': [
        'assailant',
        'was_journalist_targeted',
    ],
    'Subpoena / Legal Order': [
        'subpoena_type',
        'subpoena_status',
        'held_in_contempt',
        'detention_status',
    ],
}


class Filter(object):
    def __init__(self, name, model_field, lookup=None):
        self.name = name
        self.model_field = model_field
        self.lookup = lookup or name

    def get_value(self, data):
        return data.get(self.name) or None

    def clean(self, value):
        return self.model_field.to_python(value)

    def filter(self, queryset, value):
        """
        Filter the queryset according to the given (cleaned) value.

        This will only get called if value is not None.
        """
        return queryset.filter(**{self.lookup: value})

    def __repr__(self):
        return '<{}: {}>'.format(
            self.__class__.__name__,
            self.name,
        )


class DateFilter(Filter):
    def __init__(self, *args, fuzzy=False, **kwargs):
        self.fuzzy = fuzzy
        super(DateFilter, self).__init__(*args, **kwargs)

    def get_value(self, data):
        start = data.get('{}_lower'.format(self.name)) or None
        end = data.get('{}_upper'.format(self.name)) or None
        return start, end

    def clean(self, value):
        start, end = value

        start = self.model_field.to_python(start)
        end = self.model_field.to_python(end)

        if start and end and start > end:
            value = None
        elif start or end:
            value = (start, end)
        else:
            value = None

        return value

    def filter(self, queryset, value):
        lower_date, upper_date = value

        if lower_date == upper_date:
            return queryset.filter(**{self.lookup: lower_date})

        if self.fuzzy:
            queryset = queryset.annotate(
                fuzzy_date=MakeDateRange(
                    Cast(Trunc('date', 'month'), DateField()),
                    Cast(F('date') + Cast(Value('1 month'), DurationField()), DateField()),
                ),
            )
            target_range = DateRange(
                lower=lower_date,
                upper=upper_date,
                bounds='[]'
            )
            exact_date_match = Q(
                date__contained_by=target_range,
                exact_date_unknown=False,
            )

            inexact_date_match_lower = Q(
                exact_date_unknown=True,
                fuzzy_date__overlap=target_range,
            )

            return queryset.filter(exact_date_match | inexact_date_match_lower)

        return queryset.filter(**{
            '{0}__contained_by'.format(self.lookup): DateRange(
                lower=lower_date,
                upper=upper_date,
                bounds='[]'
            )
        })


class ChoiceFilter(Filter):
    def get_choices(self):
        return {choice[0] for choice in self.model_field.choices}

    def clean(self, value):
        if not value:
            return None
        values = value.split(',')
        value = [v for v in values if v in self.get_choices()]
        return value or None

    def filter(self, queryset, value):
        return queryset.filter(**{'{}__in'.format(self.lookup): value})


class ManyRelationFilter(Filter):
    def clean(self, value):
        if not value:
            return None
        values = value.split(',')

        value = []
        for v in values:
            try:
                value.append(int(v))
            except ValueError:
                continue
        return value

    def filter(self, queryset, value):
        return queryset.filter(**{'{}__in'.format(self.lookup): value})


class SearchFilter(Filter):
    def __init__(self):
        super(SearchFilter, self).__init__('search', CharField())

    def filter(self, queryset, value):
        return queryset.search(value, order_by_relevance=False)


class ChargesFilter(ManyRelationFilter):
    def filter(self, queryset, value):
        dropped_charges_match = Q(dropped_charges__in=value)
        current_charges_match = Q(current_charges__in=value)
        return queryset.filter(current_charges_match | dropped_charges_match)


class CircuitsFilter(ChoiceFilter):
    def get_choices(self):
        return set(STATES_BY_CIRCUIT)

    def filter(self, queryset, value):
        states = set()
        for circuit in value:
            states |= STATES_BY_CIRCUIT[circuit]

        return queryset.filter(state__name__in=states)


class IncidentFilter(object):
    base_filters = (
        'affiliation',
        'categories',
        'city',
        'date',
        'state',
        'tags',
        'targets',
        'lawsuit_name',
        'venue',
    )

    filter_overrides = {
        'circuits': {'filter_cls': CircuitsFilter},
        'charges': {'filter_cls': ChargesFilter},
        'date': {'fuzzy': True},
        'equipment_seized': {'lookup': 'equipment_seized__equipment'},
        'equipment_broken': {'lookup': 'equipment_broken__equipment'},
        'categories': {'lookup': 'categories__category'},
    }

    def __init__(self, data):
        self.data = data
        self.cleaned_data = None
        self.search_filter = None
        self.filters = None

    @classmethod
    def from_request(cls, request):
        return cls(request.GET)

    def _get_filters(self, field_names):
        filters = []
        for name in field_names:
            model_field = IncidentPage._meta.get_field(name)

            kwargs = {
                'filter_cls': Filter,
                'name': name,
                'model_field': model_field,
            }

            if isinstance(model_field, (ManyToManyField, ManyToOneRel)):
                kwargs['filter_cls'] = ManyRelationFilter
            elif isinstance(model_field, DateField):
                kwargs['filter_cls'] = DateFilter
            elif model_field.choices:
                kwargs['filter_cls'] = ChoiceFilter

            if name in self.filter_overrides:
                kwargs.update(self.filter_overrides[name])

            filter_cls = kwargs.pop('filter_cls')
            filters.append(filter_cls(**kwargs))
        return filters

    def clean(self):
        self.cleaned_data = {}

        self.search_filter = SearchFilter()
        self.filters = self._get_filters(self.base_filters)

        for f in [self.search_filter] + self.filters:
            try:
                cleaned_value = f.clean(f.get_value(self.data))
                if cleaned_value is not None:
                    self.cleaned_data[f.name] = cleaned_value
            except ValidationError:
                pass

        category_ids = self.cleaned_data.get('categories')
        if category_ids:
            categories = CategoryPage.objects.live().filter(id__in=category_ids)
            category_filters = self._get_filters((
                f
                for category in categories
                for f in CATEGORIES.get(category.title, [])
            ))
            self.filters += category_filters
            for f in category_filters:
                try:
                    cleaned_value = f.clean(f.get_value(self.data))
                    if cleaned_value is not None:
                        self.cleaned_data[f.name] = cleaned_value
                except ValidationError:
                    pass

    def get_category_options(self):
        return [
            dict(id=page.id, title=page.title, url=page.url, related_fields=page.get_incident_fields_dict())
            for page in CategoryPage.objects.live()
        ]

    def _get_queryset(self):
        if self.cleaned_data is None:
            self.clean()

        queryset = IncidentPage.objects.live()

        for f in self.filters:
            cleaned_value = self.cleaned_data.get(f.name)
            if cleaned_value is not None:
                queryset = f.filter(queryset, cleaned_value)

        return queryset.distinct()

    def get_queryset(self):
        queryset = self._get_queryset().order_by('-date', 'path').distinct()

        search = self.cleaned_data.get('search')
        if search:
            queryset = self.search_filter.filter(queryset, search)

        return queryset

    def get_summary(self):
        """
        Return a tuple of (label, value) pairs with summary data of the
        incidents.

        The data this chooses to summarize is based on the presence and value
        of particular filters.

        """
        queryset = self._get_queryset()

        TODAY = date.today()
        THIS_YEAR = TODAY.year
        THIS_MONTH = TODAY.month

        summary = (
            ('Total Results', queryset.count()),
        )

        # Add counts for this year and this month if non-zero
        incidents_this_year = queryset.filter(date__contained_by=DateRange(
            TODAY.replace(month=1, day=1),
            TODAY.replace(month=12, day=31),
            bounds='[]'
        ))

        # Only increment month if there's another month in the year.
        if THIS_MONTH < 12:
            next_month = THIS_MONTH + 1
        else:
            next_month = THIS_MONTH

        incidents_this_month = queryset.filter(date__contained_by=DateRange(
            TODAY.replace(day=1),
            TODAY.replace(month=next_month, day=1),
            bounds='[)'
        ))

        search = self.cleaned_data.get('search')
        if search:
            incidents_this_year = self.search_filter.filter(incidents_this_year, search)
            incidents_this_month = self.search_filter.filter(incidents_this_month, search)
        num_this_year = incidents_this_year.count()
        num_this_month = incidents_this_month.count()

        if num_this_year > 0:
            summary = summary + ((
                'Results in {}'.format(THIS_YEAR),
                num_this_year
            ),)

        if num_this_month > 0:
            summary = summary + ((
                'Results in {0:%B}'.format(TODAY),
                num_this_month
            ),)

        # If more than one category is included in this set, add a summary item
        # for each category of the form ("Total <Category Name>", <Count>)
        category_pks = self.cleaned_data.get('categories')
        if category_pks:
            categories = CategoryPage.objects.filter(
                pk__in=category_pks
            ).annotate(num_incidents=Count('incidents'))
            for category in categories:
                summary = summary + ((
                    category.plural_name if category.plural_name else category.title,
                    category.num_incidents,
                ),)

        return summary
