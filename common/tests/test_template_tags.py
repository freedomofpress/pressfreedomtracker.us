from unittest import mock

from django.test import TestCase

from common.templatetags.common_tags import lookup, add_as_string


class TestTemplateTags(TestCase):
    def test_lookup(self):
        obj = {
            'some_key': 'some_value'
        }

        self.assertEqual(lookup(obj, 'some_key'), 'some_value')

    def test_lookup_not_found_returns_empty_string(self):
        obj = {
            'some_key': 'some_value'
        }

        self.assertEqual(lookup(obj, 'some_other_key'), '')

    def test_add_as_string(self):
        part_string = 'A value with a number at the end: '
        whole_string = 'A value with a number at the end: 2'

        self.assertEqual(add_as_string(part_string, 2), whole_string)

    def test_add_as_string_multiple_coercion_errors_returns_empty_string(self):
        part_string = 'A value with a number at the end: '
        bad_object = mock.MagicMock()
        bad_object.__str__.side_effect = ValueError
        bad_object.__radd__.side_effect = ValueError

        self.assertEqual(add_as_string(part_string, bad_object), '')

    def test_add_as_string_single_coercion_error_defaults_to_addition(self):
        part_string = 'A value with a number at the end: '
        bad_object = mock.MagicMock()
        bad_object.__str__.side_effect = TypeError
        bad_object.__radd__.return_value = 'I was added to something'

        self.assertEqual(add_as_string(part_string, bad_object), 'I was added to something')
