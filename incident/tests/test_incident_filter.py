from django.db.models import TextField
from django.test import TestCase
from wagtail.wagtailcore.fields import RichTextField, StreamField

from common.tests.factories import CategoryPageFactory
from incident.models import IncidentPage
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
        })

    def test_field_without_verbose_name(self):
        field = IncidentPage._meta.get_field('city')
        filter_ = IncidentFilter._get_filter(field)
        self.assertEqual(filter_.serialize(), {
            'title': 'city',
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
            'title': 'Politicians or public officials involved',
            'type': 'autocomplete',
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
    def setUp(self):
        self.category = CategoryPageFactory(
            title='Denial of Access',
            incident_filters=['politicians_or_public_figures_involved'],
        )

    def test_base_filters_only(self):
        incident_filter = IncidentFilter({})
        incident_filter.clean()
        self.assertEqual(
            {f.name for f in incident_filter.filters},
            set(IncidentFilter.base_filters),
        )

    def test_includes_category_filters(self):
        incident_filter = IncidentFilter({
            'categories': str(self.category.id),
        })
        incident_filter.clean()
        self.assertEqual(
            {f.name for f in incident_filter.filters},
            set(IncidentFilter.base_filters) | {'politicians_or_public_figures_involved'},
        )


class CleanTest(TestCase):
    def test_only_clean_provided_data(self):
        category = CategoryPageFactory(incident_filters=['is_search_warrant_obtained'])
        incident_filter = IncidentFilter({
            'categories': str(category.id),
        })
        incident_filter.clean(strict=True)

        self.assertEqual(incident_filter.cleaned_data, {
            'categories': [category.id],
        })
