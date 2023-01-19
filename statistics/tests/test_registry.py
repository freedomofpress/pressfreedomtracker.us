from unittest import mock

from django.test import TestCase

from statistics.registry import get_numbers_default


class TestGetNumbers(TestCase):
    def test_no_numbers_registered_should_have_default_value_of_empty_string(self):
        with mock.patch('statistics.registry.NUMBERS', {}):
            self.assertEqual(get_numbers_default(), '')

    def test_some_numbers_registered_should_have_default_value_of_first_number(self):
        mock_numbers = {
            'num_targets': lambda: None,
            'num_people': lambda x: None,
        }
        with mock.patch('statistics.registry.NUMBERS', mock_numbers):
            self.assertEqual(get_numbers_default(), 'num_targets')
