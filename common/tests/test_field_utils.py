from django.test import TestCase
from common.utils.fields import remove_unwanted_fields, get_field_tuple, get_field_type
from incident.models import IncidentPage


class TestRemoveUnwantedFields(TestCase):
    def test_returns_true_if_field_is_valid(self):
        included_field = IncidentPage._meta.get_field('arrest_status')
        self.assertTrue(remove_unwanted_fields(included_field))

    def test_returns_false_if_field_is_invalid(self):
        blacklisted_field = IncidentPage._meta.get_field('page_ptr')
        self.assertFalse(remove_unwanted_fields(blacklisted_field))

    def test_returns_false_if_inline_field_is_invalid(self):
        blacklisted_field = IncidentPage._meta.get_field('categories')
        self.assertFalse(remove_unwanted_fields(blacklisted_field))


class TestGetFieldTuple(TestCase):
    def test_field_with_verbose_name(self):
        field = IncidentPage._meta.get_field('arrest_status')
        expected = (field.name, field.verbose_name)
        self.assertEqual(
            get_field_tuple(field),
            expected
        )

    def test_field_without_verbose_name(self):
        field = IncidentPage._meta.get_field('city')
        expected = (field.name, field.name)
        self.assertEqual(
            get_field_tuple(field),
            expected
        )

    def test_inline_field(self):
        field = IncidentPage._meta.get_field('equipment_seized')
        expected = (field.name, field.related_model._meta.verbose_name)
        self.assertEqual(
            get_field_tuple(field),
            expected
        )


class TestGetFieldType(TestCase):
    def test_radio_field(self):
        field = IncidentPage._meta.get_field('was_journalist_targeted')
        self.assertEqual(get_field_type(field), 'radio')

    def test_choice_field(self):
        field = IncidentPage._meta.get_field('status_of_charges')
        self.assertEqual(get_field_type(field), 'choice')

    def test_date_field(self):
        field = IncidentPage._meta.get_field('release_date')
        self.assertEqual(get_field_type(field), 'date')

    def test_bool_field(self):
        field = IncidentPage._meta.get_field('is_search_warrant_obtained')
        self.assertEqual(get_field_type(field), 'bool')

    def test_autocomplete_field(self):
        field = IncidentPage._meta.get_field('politicians_or_public_figures_involved')
        self.assertEqual(get_field_type(field), 'autocomplete')

    def test_invalid_field(self):
        field = IncidentPage._meta.get_field('body')
        self.assertEqual(get_field_type(field), "<class 'wagtail.wagtailcore.fields.StreamField'>")
