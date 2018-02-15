from unittest import TestCase

from django.core.exceptions import ValidationError

from common.validators import TemplateValidator


class TemplateValidatorTest(TestCase):
    def test_empty_template(self):
        validator = TemplateValidator()
        value = ''
        validator(value)

    def test_syntax_error(self):
        validator = TemplateValidator()
        value = '{{ }}'
        with self.assertRaises(ValidationError) as cm:
            validator(value)

        self.assertEqual(cm.exception.message, 'Empty variable tag on line 1')

    def test_invalid_tag_syntax(self):
        validator = TemplateValidator()
        value = '{% now %}'
        with self.assertRaises(ValidationError) as cm:
            validator(value)

        self.assertEqual(cm.exception.message, "'now' statement takes one argument")

    def test_allowed_builtin_tag(self):
        validator = TemplateValidator()
        value = '{% now "jS F Y H:i" %}'
        validator(value)

    def test_disallowed_builtin_tag(self):
        validator = TemplateValidator()
        value = '{% load statistics_tags %}'
        expected_msg = '{} tags are not allowed'.format(', '.join(TemplateValidator.disallowed_tags))
        with self.assertRaises(ValidationError) as cm:
            validator(value)

        self.assertEqual(cm.exception.message, expected_msg)

    def test_allows_statistics_tag(self):
        validator = TemplateValidator()
        value = '{% num_arrests %}'
        validator(value)
