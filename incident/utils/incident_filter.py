import functools
import operator
from datetime import date
import copy

from django.core.exceptions import ValidationError
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import (
    BooleanField,
    CharField,
    DateField,
    DurationField,
    ForeignKey,
    ManyToManyField,
    OuterRef,
    PositiveSmallIntegerField,
    Q,
    Subquery,
    TextField,
    Value,
)
from django.db.models.functions import Trunc, TruncMonth, Cast
from django.db.models.fields.related import ManyToOneRel
from django.utils.text import capfirst
from psycopg2.extras import DateRange
from wagtail.core.fields import RichTextField, StreamField

from incident.circuits import STATES_BY_CIRCUIT
from incident.utils.db import MakeDateRange


class Filter(object):
    serialized_type = 'text'

    def __init__(self, name, model_field, lookup=None, verbose_name=None):
        self.name = name
        self.model_field = model_field
        self._lookup = lookup
        self.verbose_name = verbose_name

    def __repr__(self):
        return '<{}: {}>'.format(
            self.__class__.__name__,
            self.name,
        )

    def get_value(self, data):
        return data.get(self.name) or None

    @property
    def lookup(self):
        return self._lookup or self.name

    def clean(self, value, strict=False):
        return self.model_field.to_python(value)

    def get_allowed_parameters(self):
        return {self.name}

    def get_query_arguments(self, value):
        """Returns the give value as a Django Q-object appropriate for the
filtering query."""
        return Q(**{self.lookup: value})

    def filter(self, queryset, value):
        """
        Filter the queryset according to the given (cleaned) value.

        This will only get called if value is not None.
        """
        return queryset.filter(self.get_query_arguments(value))

    def get_verbose_name(self):
        return self.verbose_name or self.model_field.verbose_name

    def serialize(self):
        serialized = {
            'title': capfirst(self.get_verbose_name()),
            'type': self.serialized_type,
            'name': self.name,
        }
        return serialized


class BooleanFilter(Filter):
    serialized_type = 'bool'


class IntegerFilter(Filter):
    serialized_type = 'int'


class RelationFilter(Filter):
    serialized_type = 'autocomplete'

    def __init__(self, name, model_field, lookup=None, verbose_name=None, text_fields=[]):
        self.text_fields = text_fields
        super().__init__(name, model_field, lookup=lookup, verbose_name=verbose_name)

    def get_query_arguments(self, value):
        if isinstance(value, int):
            return super().get_query_arguments(value)
        else:
            arguments = [
                Q(**{f'{self.name}__{field}__iexact': value}) for field in self.text_fields
            ]
            return functools.reduce(operator.or_, arguments)

    def clean(self, value, strict=False):
        try:
            return int(value)
        except ValueError:
            if self.text_fields:
                # If this filter supports fallback text fields for
                # filtering non-integer ID values, return whatever we
                # were given.
                return value
            elif strict:
                raise ValidationError(
                    'Expected integer for relationship "{}", received "{}"'.format(
                        self.name,
                        value,
                    )
                )
            else:
                return None

    def serialize(self):
        serialized = super(RelationFilter, self).serialize()
        related_model = self.model_field.remote_field.model
        serialized['autocomplete_type'] = '{}.{}'.format(
            related_model._meta.app_label,
            related_model.__name__,
        )
        serialized['many'] = False
        return serialized


class DateFilter(Filter):
    serialized_type = 'date'

    def __init__(self, name, model_field, lookup=None, verbose_name=None, fuzzy=False):
        self.fuzzy = fuzzy
        super(DateFilter, self).__init__(name, model_field, lookup=lookup, verbose_name=verbose_name)

    def get_value(self, data):
        start = data.get('{}_lower'.format(self.name)) or None
        end = data.get('{}_upper'.format(self.name)) or None
        return start, end

    def get_verbose_name(self):
        if self.verbose_name:
            return self.verbose_name
        return '{} between'.format(super(DateFilter, self).get_verbose_name())

    def clean(self, value, strict=False):
        start, end = value

        start = self.model_field.to_python(start)
        end = self.model_field.to_python(end)

        if start and end and start > end:
            value = None
            if strict:
                raise ValidationError('{}_lower must be less than or equal to {}_upper'.format(
                    self.name,
                    self.name,
                ))
        elif start or end:
            value = (start, end)
        else:
            # No error raised here because 'no value' is okay.
            value = None

        return value

    def get_allowed_parameters(self):
        return {'{}_lower'.format(self.name), '{}_upper'.format(self.name)}

    def filter(self, queryset, value):
        lower_date, upper_date = value

        if lower_date == upper_date:
            return queryset.filter(**{self.lookup: lower_date})

        if self.fuzzy:
            queryset = queryset.annotate(
                fuzzy_date=MakeDateRange(
                    Cast(Trunc('date', 'month'), DateField()),
                    Cast(TruncMonth('date') + Cast(Value('1 month'), DurationField()), DateField()),
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
    @property
    def serialized_type(self):
        choices = self.get_choices()
        if 'JUST_TRUE' in choices:
            return 'radio'
        return 'choice'

    def get_choices(self):
        return {choice[0] for choice in self.model_field.choices}

    def clean(self, value, strict=False):
        if not value:
            return None
        values = value.split(',')
        value = []
        invalid_values = []
        choices = self.get_choices()

        for v in values:
            if v in choices:
                value.append(v)
            else:
                invalid_values.append(v)

        if invalid_values and strict:
            raise ValidationError('Invalid value{} for {}: {}'.format(
                's' if len(invalid_values) != 1 else '',
                self.name,
                ','.join(invalid_values),
            ))
        return value or None

    def filter(self, queryset, value):
        return queryset.filter(**{'{}__in'.format(self.lookup): value})

    def serialize(self):
        serialized = super(ChoiceFilter, self).serialize()
        if serialized['type'] == 'choice':
            serialized['choices'] = self.model_field.choices
        return serialized


class MultiChoiceFilter(Filter):
    serialized_type = 'choice'

    def clean(self, value, strict=False):
        choices = self.get_choices()
        if not value:
            return None
        values = value.split(',')
        value = []
        invalid_values = []
        choices = self.get_choices()

        for v in values:
            if v in choices:
                value.append(v)
            else:
                invalid_values.append(v)

        if invalid_values and strict:
            raise ValidationError('Invalid value{} for {}: {}'.format(
                's' if len(invalid_values) != 1 else '',
                self.name,
                ','.join(invalid_values),
            ))
        return value or None

    def get_choices(self):
        return {choice[0] for choice in self.model_field.base_field.choices}

    def filter(self, queryset, values):
        queryset_initial = queryset
        for key, value in enumerate(values):
            if key == 0:
                queryset = queryset_initial.filter(**{'{}__contains'.format(self.lookup): [value]})
            else:
                queryset |= queryset_initial.filter(**{'{}__contains'.format(self.lookup): [value]})
        return queryset.distinct()

    def serialize(self):
        serialized = super(MultiChoiceFilter, self).serialize()
        if serialized['type'] == 'choice':
            serialized['choices'] = self.model_field.base_field.choices
        return serialized


class ManyRelationFilter(Filter):
    serialized_type = 'autocomplete'

    def clean(self, value, strict=False):
        if not value:
            return None
        if isinstance(value, int):
            values = [value]
        else:
            values = value.split(',')
        invalid_values = []

        value = []
        for v in values:
            try:
                value.append(int(v))
            except ValueError:
                invalid_values.append(v)

        if invalid_values and strict:
            raise ValidationError('Invalid value{} for {}: {}'.format(
                's' if len(invalid_values) != 1 else '',
                self.name,
                ','.join(invalid_values),
            ))
        return value

    def filter(self, queryset, value):
        return queryset.filter(**{'{}__in'.format(self.lookup): value})

    def get_verbose_name(self):
        if self.verbose_name:
            return self.verbose_name
        if hasattr(self.model_field, 'verbose_name'):
            return self.model_field.verbose_name
        return self.model_field.related_model._meta.verbose_name

    def serialize(self):
        serialized = super(ManyRelationFilter, self).serialize()
        related_model = self.model_field.remote_field.model
        if isinstance(self.model_field, ManyToOneRel) and hasattr(related_model, '_autocomplete_model'):
            serialized['autocomplete_type'] = related_model._autocomplete_model
        else:
            serialized['autocomplete_type'] = '{}.{}'.format(
                related_model._meta.app_label,
                related_model.__name__,
            )
        serialized['many'] = True
        return serialized


class SearchFilter(Filter):
    def __init__(self):
        super(SearchFilter, self).__init__('search', CharField(verbose_name='search terms'))

    def filter(self, queryset, value):
        query = SearchQuery(value)
        vector = SearchVector('title', 'body')
        return queryset.annotate(search=vector).filter(search=query)


class ChargesFilter(ManyRelationFilter):
    def filter(self, queryset, value):
        dropped_charges_match = Q(dropped_charges__in=value)
        current_charges_match = Q(current_charges__in=value)
        return queryset.filter(current_charges_match | dropped_charges_match)

    def serialize(self):
        serialized = super(ManyRelationFilter, self).serialize()
        serialized['autocomplete_type'] = 'incident.Charge'
        return serialized


class RelationThroughFilter(ManyRelationFilter):
    def __init__(self, name, model_field, relation, lookup=None, verbose_name=None):
        lookup = model_field.name + '__' + relation
        super(RelationThroughFilter, self).__init__(name, model_field, lookup, verbose_name)
        self.relation = relation

    def serialize(self):
        serialized = super(ManyRelationFilter, self).serialize()

        related_model = self.model_field.remote_field.model._meta.get_field(self.relation).target_field.model

        if isinstance(self.model_field, ManyToOneRel) and hasattr(related_model, '_autocomplete_model'):
            serialized['autocomplete_type'] = related_model._autocomplete_model
        else:
            serialized['autocomplete_type'] = '{}.{}'.format(
                related_model._meta.app_label,
                related_model.__name__,
            )
        serialized['many'] = True
        return serialized


class CircuitsFilter(ChoiceFilter):
    def get_choices(self):
        return set(STATES_BY_CIRCUIT)

    def filter(self, queryset, value):
        states = set()
        for circuit in value:
            states |= set(STATES_BY_CIRCUIT[circuit])

        return queryset.filter(state__name__in=states)


class PendingCasesFilter(BooleanFilter):
    """
    Multi-field filter. Finds incidents with any of the following:
    - arrest_status: DETAINED_CUSTODY
    - arrest_status: ARRESTED_CUSTODY
    - status_of_charges: CHARGES_PENDING
    - status_of_charges: PENDING_APPEAL
    - status_of_seized_equipment: CUSTODY
    - status_of_seized_equipment: RETURNED_PART
    - subpoena_status: PENDING
    - detention_status: IN_JAIL
    - status_of_prior_restraint: PENDING
    """
    def __init__(self, name, verbose_name=None):
        super(PendingCasesFilter, self).__init__(
            name=name,
            model_field=BooleanField(),
            verbose_name=verbose_name,
        )

    def filter(self, queryset, value):
        if not value:
            return queryset

        return queryset.filter(
            Q(arrest_status='DETAINED_CUSTODY') |
            Q(arrest_status='ARRESTED_CUSTODY') |
            Q(status_of_charges='CHARGES_PENDING') |
            Q(status_of_charges='PENDING_APPEAL') |
            Q(status_of_seized_equipment='CUSTODY') |
            Q(status_of_seized_equipment='RETURNED_PART') |
            Q(subpoena_statuses__contains=['PENDING']) |
            Q(detention_status='IN_JAIL') |
            Q(status_of_prior_restraint='PENDING')
        )


class RecentlyUpdatedFilter(IntegerFilter):
    def __init__(self, name, verbose_name=None):
        super(RecentlyUpdatedFilter, self).__init__(
            name=name,
            model_field=PositiveSmallIntegerField(),
            verbose_name=verbose_name,
        )

    def serialize(self):
        serialized = super(RecentlyUpdatedFilter, self).serialize()
        serialized['units'] = 'days'
        return serialized

    def filter(self, queryset, value):
        return queryset.with_most_recent_update().updated_within_days(value)


class TargetedInstitutionsFilter(ManyRelationFilter):
    def filter(self, queryset, value):
        return queryset.filter(
            Q(targeted_journalists__institution__in=value) | Q(targeted_institutions__in=value)
        )


def get_serialized_filters():
    """
    Returns filters serialized to be passed as JSON to the front-end.
    """
    from common.models import CategoryPage, GeneralIncidentFilter
    available_filters = IncidentFilter.get_available_filters()
    general_incident_filters = GeneralIncidentFilter.objects.all()
    return [
        {
            'id': -1,
            'title': 'General',
            'filters': [
                SearchFilter().serialize()
            ] + [
                available_filters[obj.incident_filter].serialize()
                for obj in general_incident_filters
                if obj.incident_filter in available_filters
            ],
        },
    ] + [
        {
            'id': page.id,
            'title': page.title,
            'url': page.url,
            'filters': [
                available_filters[obj.incident_filter].serialize()
                for obj in page.incident_filters.all()
                if obj.incident_filter in available_filters
            ],
        }
        for page in CategoryPage.objects.live().prefetch_related('incident_filters')
    ]


class IncidentFilter(object):
    filter_overrides = {
        'categories': {'lookup': 'categories__category'},
        'date': {'fuzzy': True, 'verbose_name': 'took place between'},
        'city': {'lookup': 'city__iexact'},
        'equipment_seized': {'lookup': 'equipment_seized__equipment'},
        'equipment_broken': {'lookup': 'equipment_broken__equipment'},
        'tags': {'verbose_name': 'Has any of these tags'},
        'subpoena_statuses': {'verbose_name': 'Subpoena status'},
        'targeted_journalists': {'verbose_name': 'Targeted any of these journalists', 'filter_cls': RelationThroughFilter, 'relation': 'journalist'},
        'targeted_institutions': {'filter_cls': TargetedInstitutionsFilter},
        'arresting_authority': {'filter_cls': RelationFilter, 'verbose_name': 'Arresting authority'},
        'venue': {'filter_cls': RelationFilter, 'verbose_name': 'venue'},
        'state': {'text_fields': ['abbreviation', 'name']}
    }

    _extra_filters = {
        'circuits': CircuitsFilter(name='circuits', model_field=CharField(verbose_name='circuits')),
        'charges': ChargesFilter(name='charges', model_field=CharField(verbose_name='charges')),
        'pending_cases': PendingCasesFilter(name='pending_cases', verbose_name='Show only pending cases'),
        'recently_updated': RecentlyUpdatedFilter(name='recently_updated', verbose_name='Updated in the last')
    }

    # IncidentPage fields that cannot be filtered on.
    # RichTextFields, TextFields, and StreamFields can never be filtered on,
    # regardless of whether they're in this list or not.
    exclude_fields = {
        'page_ptr',
        'exact_date_unknown',
        'teaser_image',
        'related_incidents',
        'updates',
        'search_image',
        'longitude',
        'latitude',
    }

    def __init__(self, data):
        self.data = data
        self.cleaned_data = None
        self.errors = None
        self.search_filter = None
        self.filters = None

    @classmethod
    def get_available_filters(cls):
        """
        Returns a dictionary mapping filter names to filter instances.
        """
        # Prevent circular imports
        from incident.models.incident_page import IncidentPage

        filters = copy.deepcopy(cls._extra_filters)

        fields = IncidentPage._meta.get_fields(include_parents=False)
        for field in fields:
            if isinstance(field, (RichTextField, StreamField, TextField)):
                continue
            if field.name in cls.exclude_fields:
                continue
            filters[field.name] = cls._get_filter(field)
        return filters

    @classmethod
    def get_filter_choices(cls):
        return FilterChoicesIterator()

    @classmethod
    def _get_filter(cls, model_field):
        kwargs = {
            'filter_cls': Filter,
            'name': model_field.name,
            'model_field': model_field,
        }

        from incident.models import ChoiceArrayField

        if isinstance(model_field, (ManyToManyField, ManyToOneRel)):
            kwargs['filter_cls'] = ManyRelationFilter
        elif isinstance(model_field, ForeignKey):
            kwargs['filter_cls'] = RelationFilter
        elif isinstance(model_field, DateField):
            kwargs['filter_cls'] = DateFilter
        elif model_field.choices:
            kwargs['filter_cls'] = ChoiceFilter
        elif isinstance(model_field, ChoiceArrayField):
            kwargs['filter_cls'] = MultiChoiceFilter
        elif isinstance(model_field, BooleanField):
            kwargs['filter_cls'] = BooleanFilter

        if model_field.name in cls.filter_overrides:
            kwargs.update(cls.filter_overrides[model_field.name])

        filter_cls = kwargs.pop('filter_cls')
        return filter_cls(**kwargs)

    def _clean_filter(self, filter_, strict):
        value = filter_.get_value(self.data)
        if value is not None:
            cleaned_value = filter_.clean(value, strict=strict)
            if cleaned_value is not None:
                self.cleaned_data[filter_.name] = cleaned_value

    def clean(self, strict=False):
        """
        Validates data and convert it to a useable python format. If strict is True,
        raises a ValidationError for errors; otherwise the fields with errors
        are simply ignored.
        """
        from common.models import CategoryPage, GeneralIncidentFilter
        self.cleaned_data = {}
        errors = []

        # Keep track of search filter so that we can handle search separately later.
        # This is necessary because search has to happen after _all_ filtering.
        self.search_filter = SearchFilter()

        available_filters = IncidentFilter.get_available_filters()
        categories_filter = available_filters.pop('categories')

        self.filters = [
            categories_filter,
            self.search_filter,
        ]

        # Collect filters for categories. If categories are selected,
        # use their filters; otherwise use filters for all categories.
        # Clean categories first so that we can check for category ids.
        try:
            self._clean_filter(categories_filter, strict=strict)
        except ValidationError as exc:
            errors.append(exc)

        categories = CategoryPage.objects.live().prefetch_related(
            'incident_filters',
        )
        category_ids = self.cleaned_data.get('categories')
        if category_ids:
            categories = categories.filter(
                id__in=category_ids,
            )
        for category in categories:
            for category_incident_filter in category.incident_filters.all():
                incident_filter = category_incident_filter.incident_filter
                if incident_filter in available_filters:
                    self.filters.append(available_filters[incident_filter])

        # Collect filters from general settings.
        general_incident_filters = GeneralIncidentFilter.objects.all()
        for general_incident_filter in general_incident_filters:
            incident_filter = general_incident_filter.incident_filter
            if incident_filter in available_filters:
                self.filters.append(available_filters[incident_filter])

        # Clean collected filters.
        for f in self.filters:
            try:
                self._clean_filter(f, strict=strict)
            except ValidationError as exc:
                errors.append(exc)

        # If strict is true, validate that all given filters are valid
        # and raise ValidationError if there are any errors.
        if strict:
            allowed_parameters = set()
            for f in self.filters:
                allowed_parameters |= f.get_allowed_parameters()

            disallowed_parameters = set()
            for f in available_filters.values():
                disallowed_parameters |= f.get_allowed_parameters()
            disallowed_parameters -= allowed_parameters

            params_requiring_category = set(self.data) & disallowed_parameters
            if params_requiring_category:
                filters_requiring_category = {
                    f for f in available_filters.values()
                    if f.get_allowed_parameters() & params_requiring_category
                }

                for f in filters_requiring_category:
                    category = CategoryPage.objects.live().filter(
                        incident_filters__incident_filter=f.name,
                    ).first()
                    if category:
                        errors.append('{} filter only available when filtering on the following category: {} ({})'.format(
                            f.name,
                            category.title,
                            category.id,
                        ))
                    else:
                        errors.append('{} filter only available when filtering on a category which provides it (but no category currently does)'.format(f.name))

            invalid_parameters = set(self.data) - allowed_parameters - params_requiring_category
            if invalid_parameters:
                errors.append('Invalid parameter{} provided: {}'.format(
                    's' if len(invalid_parameters) != 1 else '',
                    ','.join(invalid_parameters),
                ))

            if errors:
                raise ValidationError(errors)

    def _get_queryset(self):
        # Prevent circular imports
        from incident.models.incident_page import IncidentPage
        if self.cleaned_data is None:
            self.clean()

        queryset = IncidentPage.objects.live()

        for f in self.filters:
            cleaned_value = self.cleaned_data.get(f.name)
            if cleaned_value is not None:
                queryset = f.filter(queryset, cleaned_value)

        return queryset.distinct()

    def get_queryset(self):
        return self._get_queryset().order_by('-date', 'path').distinct()

    def get_summary(self):
        """
        Return a tuple of (label, value) pairs with summary data of the
        incidents.

        The data this chooses to summarize is based on the presence and value
        of particular filters.

        """
        from common.models import CategoryPage
        from incident.models.items import Institution, TargetedJournalist, Journalist
        queryset = self._get_queryset()

        TODAY = date.today()
        THIS_YEAR = TODAY.year

        # Add counts for this year and this month if non-zero
        incidents_this_year = queryset.filter(date__contained_by=DateRange(
            TODAY.replace(month=1, day=1),
            TODAY.replace(month=12, day=31),
            bounds='[]'
        ))

        incidents_this_month = queryset.filter(
            date__month=TODAY.month,
            date__year=TODAY.year,
        )

        incident_ids = list(queryset.values_list('pk', flat=True))
        num_this_year = incidents_this_year.count()
        num_this_month = incidents_this_month.count()

        tj_queryset = TargetedJournalist.objects.filter(incident__in=incident_ids)
        tj_inst_queryset = tj_queryset.filter(
            institution_id=OuterRef('pk')
        ).values_list('institution_id', flat=True)

        summary = (
            ('Total Results', len(incident_ids)),
            ('Journalists affected', Journalist.objects.filter(targeted_incidents__in=tj_queryset).distinct().count()),
            ('Institutions affected', Institution.objects.filter(
                Q(institutions_incidents__in=incident_ids) | Q(id__in=Subquery(tj_inst_queryset))
            ).distinct().count()),
        )

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
        if category_pks and len(category_pks) > 1:
            categories = CategoryPage.objects.filter(
                pk__in=category_pks
            )
            for category in categories:
                category_queryset = queryset.filter(categories__category=category)
                summary = summary + ((
                    category.plural_name if category.plural_name else category.title,
                    category_queryset.count(),
                ),)

        return summary


class FilterChoicesIterator(object):
    """
    Helper class to get around circular imports.
    """
    def __iter__(self):
        filter_choices = [
            (name, capfirst(filter_.get_verbose_name()))
            for name, filter_ in IncidentFilter.get_available_filters().items()
        ]
        filter_choices.sort(key=lambda item: item[1])
        for field, verbose_name in filter_choices:
            if field == 'categories':
                continue
            yield field, verbose_name
