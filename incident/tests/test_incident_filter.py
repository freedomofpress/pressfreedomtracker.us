from datetime import date
from unittest import mock

from django.core.exceptions import ValidationError
from django.db.models import TextField
from django.test import TestCase
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Site

from common.models import (
    CategoryPage,
    CategoryIncidentFilter,
    GeneralIncidentFilter,
    IncidentFilterSettings,
)
from common.tests.factories import CategoryPageFactory
from incident.models import IncidentPage
from incident.choices import ARREST_STATUS, STATUS_OF_CHARGES
from incident.utils.incident_filter import (
    IncidentFilter,
    ManyRelationFilter,
    ManyRelationValue,
)


class FilterToOpenApiParametersTest(TestCase):
    def test_boolean_field(self):
        field = IncidentPage._meta.get_field('is_search_warrant_obtained')
        fltr = IncidentFilter._get_filter(field)
        (param,) = fltr.openapi_parameters()
        self.assertEqual(param.name, 'is_search_warrant_obtained')
        self.assertEqual(param.type, OpenApiTypes.BOOL)
        self.assertEqual(param.location, OpenApiParameter.QUERY)
        self.assertEqual(param.required, False)
        self.assertEqual(param.style, None)
        self.assertEqual(param.description, 'Filter by "Search warrant obtained?"')

    def test_integer_field(self):
        fltr = IncidentFilter._extra_filters['recently_updated']
        (param,) = fltr.openapi_parameters()
        self.assertEqual(param.name, 'recently_updated')
        self.assertEqual(param.type, OpenApiTypes.INT)
        self.assertEqual(param.location, OpenApiParameter.QUERY)
        self.assertEqual(param.required, False)
        self.assertEqual(param.description, 'Include only incidents updated in the last N days')

    def test_relation_filter(self):
        field = IncidentPage._meta.get_field('state')
        fltr = IncidentFilter._get_filter(field)
        (param,) = fltr.openapi_parameters()
        self.assertEqual(param.name, 'state')
        self.assertEqual(param.type, {'oneOf': [{'type': 'string'}, {'type': 'integer'}]})

    def test_integer_only_relation_filter(self):
        field = IncidentPage._meta.get_field('state')
        fltr = IncidentFilter._get_filter(field)
        fltr.text_fields = []
        (param,) = fltr.openapi_parameters()
        self.assertEqual(param.type, OpenApiTypes.INT)

    def test_date_filter(self):
        field = IncidentPage._meta.get_field('date')
        fltr = IncidentFilter._get_filter(field)
        lower, upper = fltr.openapi_parameters()

        self.assertEqual(lower.name, 'date_lower')
        self.assertEqual(lower.type, OpenApiTypes.DATE)
        self.assertEqual(lower.location, OpenApiParameter.QUERY)
        self.assertEqual(lower.required, False)
        self.assertEqual(lower.description, 'Filter by "date is after"')

        self.assertEqual(upper.name, 'date_upper')
        self.assertEqual(upper.type, OpenApiTypes.DATE)
        self.assertEqual(upper.location, OpenApiParameter.QUERY)
        self.assertEqual(upper.required, False)
        self.assertEqual(upper.description, 'Filter by "date is before"')

    def test_choice_filter(self):
        field = IncidentPage._meta.get_field('arrest_status')
        fltr = IncidentFilter._get_filter(field)
        param, = fltr.openapi_parameters()

        self.assertEqual(param.name, 'arrest_status')
        self.assertEqual(param.enum, fltr.get_choices())

    def test_multichoice_filter(self):
        field = IncidentPage._meta.get_field('subpoena_statuses')
        fltr = IncidentFilter._get_filter(field)
        param, = fltr.openapi_parameters()

        self.assertEqual(param.name, 'subpoena_statuses')
        self.assertEqual(param.style, 'form')
        self.assertEqual(param.enum, fltr.get_choices())

    def test_many_relation_filter(self):
        field = IncidentPage._meta.get_field('politicians_or_public_figures_involved')
        fltr = IncidentFilter._get_filter(field)
        param, = fltr.openapi_parameters()

        self.assertEqual(param.name, 'politicians_or_public_figures_involved')
        self.assertEqual(param.style, 'form')
        self.assertEqual(param.explode, False)


class URLizeFilterTest(TestCase):
    """Test cases for obtaining a representation of filters as URL
    parameters/query strings."""

    def test_get_url_parameters_uncleaned(self):
        params = IncidentFilter({
            'search': 'test',
            'date_lower': '20319-10291-1022',  # invalid date should be removed
        }).get_url_parameters()

        self.assertEqual(
            params, 'search=test'
        )

    def test_boolean_field(self):
        field = IncidentPage._meta.get_field('is_search_warrant_obtained')
        filter_ = IncidentFilter._get_filter(field)

        self.assertEqual(
            filter_.as_url_parameters(True),
            {'is_search_warrant_obtained': '1'}
        )
        self.assertEqual(
            filter_.as_url_parameters(False),
            {'is_search_warrant_obtained': '0'}
        )

    def test_choice_field(self):
        field = IncidentPage._meta.get_field('did_authorities_ask_about_work')
        filter_ = IncidentFilter._get_filter(field)

        self.assertEqual(
            filter_.as_url_parameters(['JUST_TRUE']),
            {'did_authorities_ask_about_work': 'JUST_TRUE'}
        )

    def test_multichoice_field(self):
        field = IncidentPage._meta.get_field('subpoena_statuses')
        filter_ = IncidentFilter._get_filter(field)

        self.assertEqual(
            filter_.as_url_parameters(['UNKNOWN', 'PENDING']),
            {'subpoena_statuses': 'UNKNOWN,PENDING'}
        )

    def test_many_relation_field(self):
        field = IncidentPage._meta.get_field('politicians_or_public_figures_involved')
        filter_ = IncidentFilter._get_filter(field)

        value = ManyRelationValue(
            pks=[1, 2],
            strings=['Person 1', 'Person 2'],
        )
        self.assertEqual(
            filter_.as_url_parameters(value),
            {'politicians_or_public_figures_involved': '1,2,Person 1,Person 2'}
        )

    def test_date_field(self):
        field = IncidentPage._meta.get_field('detention_date')
        filter_ = IncidentFilter._get_filter(field)

        date_value = (date(2022, 2, 2), date.today())
        self.assertEqual(
            filter_.as_url_parameters(date_value),
            {
                'detention_date_lower': str(date_value[0]),
                'detention_date_upper': str(date_value[1]),
            }
        )


class SerializeFilterTest(TestCase):
    def test_field_with_verbose_name(self):
        field = IncidentPage._meta.get_field('arrest_status')
        filter_ = IncidentFilter._get_filter(field)
        self.assertEqual(filter_.serialize(), {
            'title': 'Arrest status',
            'type': 'choice',
            'name': 'arrest_status',
            'choices': ARREST_STATUS,
        })

    def test_field_without_verbose_name(self):
        field = IncidentPage._meta.get_field('city')
        filter_ = IncidentFilter._get_filter(field)
        self.assertEqual(filter_.serialize(), {
            'title': 'City',
            'type': 'text',
            'name': 'city',
        })

    def test_inline_field(self):
        field = IncidentPage._meta.get_field('equipment_seized')
        filter_ = IncidentFilter._get_filter(field)
        self.assertEqual(filter_.serialize(), {
            'title': 'Equipment Seized',
            'type': 'autocomplete',
            'autocomplete_type': 'incident.Equipment',
            'name': 'equipment_seized',
            'many': True,
            'choices': [],
        })

    def test_radio_field(self):
        field = IncidentPage._meta.get_field('was_journalist_targeted')
        filter_ = IncidentFilter._get_filter(field)
        self.assertEqual(filter_.serialize(), {
            'title': 'Was journalist targeted?',
            'type': 'radio',
            'name': 'was_journalist_targeted',
        })

    def test_choice_field(self):
        field = IncidentPage._meta.get_field('status_of_charges')
        filter_ = IncidentFilter._get_filter(field)
        self.assertEqual(filter_.serialize(), {
            'title': 'Status of charges',
            'type': 'choice',
            'name': 'status_of_charges',
            'choices': STATUS_OF_CHARGES,
        })

    def test_date_field(self):
        field = IncidentPage._meta.get_field('release_date')
        filter_ = IncidentFilter._get_filter(field)
        self.assertEqual(filter_.serialize(), {
            'title': 'Release date',
            'type': 'date',
            'name': 'release_date',
        })

    def test_bool_field(self):
        field = IncidentPage._meta.get_field('is_search_warrant_obtained')
        filter_ = IncidentFilter._get_filter(field)
        self.assertEqual(filter_.serialize(), {
            'title': 'Search warrant obtained?',
            'type': 'bool',
            'name': 'is_search_warrant_obtained',
        })

    def test_autocomplete_field(self):
        field = IncidentPage._meta.get_field('politicians_or_public_figures_involved')
        filter_ = IncidentFilter._get_filter(field)
        self.assertEqual(filter_.serialize(), {
            'title': 'Government agency or public official involved',
            'type': 'autocomplete',
            'many': True,
            'autocomplete_type': 'incident.PoliticianOrPublic',
            'name': 'politicians_or_public_figures_involved',
            'choices': [],
        })


class AvailableFiltersTest(TestCase):
    def test_excluded_fields(self):
        available_filters = IncidentFilter.get_available_filters()
        for filter_ in available_filters.values():
            self.assertNotIn(filter_.name, IncidentFilter.exclude_fields)
            self.assertNotIsInstance(filter_.model_field, (RichTextField, StreamField, TextField))


class CategoryFiltersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        CategoryIncidentFilter.objects.all().delete()
        cls.category1 = CategoryPageFactory(
            title='Denial of Access',
            incident_filters=['politicians_or_public_figures_involved'],
        )
        cls.category2 = CategoryPageFactory(
            title='Other category',
            incident_filters=['equipment_seized'],
        )
        site = Site.objects.get(is_default_site=True)
        settings = IncidentFilterSettings.for_site(site)
        GeneralIncidentFilter.objects.create(
            incident_filter_settings=settings,
            incident_filter='city',
        )

    def test_no_category_filter__includes_all(self):
        """
        If no categories are selected, allow filters from any category.
        """
        incident_filter = IncidentFilter({})
        incident_filter.clean()
        self.assertEqual(
            {f.name for f in incident_filter.filters},
            {
                'city',
                'categories',
                'politicians_or_public_figures_involved',
                'equipment_seized',
                'search',
            },
        )

    def test_includes_category_filters(self):
        """
        If a category is selected, only allow filters from that category.
        """
        incident_filter = IncidentFilter({
            'categories': str(self.category1.id),
        })
        incident_filter.clean()
        self.assertEqual(
            {f.name for f in incident_filter.filters},
            {
                'city',
                'categories',
                'politicians_or_public_figures_involved',
                'search',
            },
        )


class CleanTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        CategoryIncidentFilter.objects.all().delete()

    def test_only_clean_provided_data(self):
        category = CategoryPageFactory(incident_filters=['is_search_warrant_obtained'])
        incident_filter = IncidentFilter({
            'categories': str(category.id),
        })
        incident_filter.clean(strict=True)

        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[category.id]),
        })

    def test_param_requires_correct_category(self):
        """
        If a category is selected that doesn't provide the filter, raise
        a validation error.
        """
        CategoryPage.objects.all().delete()
        category1 = CategoryPageFactory(
            title='Category A',
            incident_filters=['release_date'],
        )
        category2 = CategoryPageFactory(
            title='Category B',
        )

        incident_filter = IncidentFilter({
            'release_date_lower': '2017-01-01',
            'categories': str(category2.id),
        })
        with self.assertRaises(ValidationError) as cm:
            incident_filter.clean(strict=True)
        self.assertEqual(
            [str(error) for error in cm.exception],
            ['release_date filter only available when filtering on the following category: {} ({})'.format(
                category1.title,
                category1.id,
            )],
        )

    def test_param_requires_category__none_found(self):
        CategoryPage.objects.all().delete()
        incident_filter = IncidentFilter({
            'release_date_lower': '2017-01-01',
        })
        with self.assertRaises(ValidationError) as cm:
            incident_filter.clean(strict=True)
        self.assertEqual(
            [str(error) for error in cm.exception],
            ['release_date filter only available when filtering on a category which provides it (but no category currently does)'],
        )

    def test_invalid_param(self):
        incident_filter = IncidentFilter({
            'not_a_parameter': 'False',
        })
        with self.assertRaises(ValidationError) as cm:
            incident_filter.clean(strict=True)
        self.assertEqual(
            [str(error) for error in cm.exception],
            ['Invalid parameter provided: not_a_parameter'],
        )

    def test_invalid_data(self):
        CategoryPage.objects.all().delete()
        CategoryPageFactory(title='Category A', incident_filters=['arrest_status'])
        incident_filter = IncidentFilter({'arrest_status': '???'})

        with self.assertRaises(ValidationError) as cm:
            incident_filter.clean(strict=True)

        self.assertEqual(
            [str(error) for error in cm.exception],
            ['Invalid value for arrest_status: ???'],
        )

    def test_text_param_for_relation_filter_without_text_fields(self):
        CategoryPage.objects.all().delete()
        CategoryPageFactory(title='Category A', incident_filters=['state'])
        incident_filter = IncidentFilter({'state': '???'})

        with mock.patch.object(IncidentFilter, 'filter_overrides', {'state': {'text_fields': []}}):
            with self.assertRaises(ValidationError) as cm:
                incident_filter.clean(strict=True)

            self.assertEqual(
                [str(error) for error in cm.exception],
                ['Expected integer for relationship "state", received "???"'],
            )

    def test_text_param_for_relation_filter_without_text_fields_not_included_in_cleaned_data(self):
        CategoryPage.objects.all().delete()
        CategoryPageFactory(title='Category A', incident_filters=['state'])
        incident_filter = IncidentFilter({'state': '???'})
        with mock.patch.object(IncidentFilter, 'filter_overrides', {'state': {'text_fields': []}}):
            incident_filter.clean(strict=False)

            self.assertEqual(incident_filter.cleaned_data, {})

    def test_text_param_for_manyrelation_filter_without_text_fields(self):
        fltr = ManyRelationFilter('venue', IncidentPage.venue, text_fields=[])

        with self.assertRaises(ValidationError) as cm:
            fltr.clean('???', strict=True)

        self.assertEqual(
            [str(error) for error in cm.exception],
            ['Invalid value for venue: ???'],
        )
