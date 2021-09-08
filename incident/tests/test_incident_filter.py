from django.core.exceptions import ValidationError
from django.db.models import TextField
from django.test import TestCase
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Site

from common.models import (
    CategoryPage,
    CategoryIncidentFilter,
    GeneralIncidentFilter,
    IncidentFilterSettings,
)
from common.tests.factories import CategoryPageFactory
from incident.models import IncidentPage
from incident.models.choices import ARREST_STATUS, STATUS_OF_CHARGES
from incident.utils.incident_filter import (
    IncidentFilter,
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
            'title': 'Release date between',
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
            'title': 'Politicians or public officials involved',
            'type': 'autocomplete',
            'many': True,
            'autocomplete_type': 'incident.PoliticianOrPublic',
            'name': 'politicians_or_public_figures_involved',
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
            'categories': [category.id],
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
