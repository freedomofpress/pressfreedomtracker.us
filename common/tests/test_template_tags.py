from django.test import TestCase

from common.templatetags.common_tags import lookup, add_as_string


class TestTemplateTags(TestCase):
    def test_lookup(self):
        obj = {
            'some_key': 'some_value'
        }

        self.assertEqual(lookup(obj, 'some_key'), 'some_value')

    def test_add_as_string(self):
        part_string = 'A value with a number at the end: '
        whole_string = 'A value with a number at the end: 2'

        self.assertEqual(add_as_string(part_string, 2), whole_string)
