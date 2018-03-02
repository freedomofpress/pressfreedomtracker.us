import datetime

from django.core.exceptions import ValidationError
from django.template import (
    Context,
    Template,
    TemplateSyntaxError,
)
from django.test import TestCase

from common.tests.factories import CategoryPageFactory
from common.validators import TemplateValidator
from incident.tests.factories import IncidentPageFactory
from statistics.templatetags.statistics_tags import (
    incidents_in_year_range_by_month,
)


class NumIncidentsTest(TestCase):
    """Test that num_incidents tag """
    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryPageFactory()
        cls.incident = IncidentPageFactory(
            title='hello',
            date=datetime.date(2017, 1, 1),
            categories=[cls.category],
        )
        cls.old_incident = IncidentPageFactory(
            title='goodbye',
            date=datetime.date(2016, 1, 1),
        )

    def setUp(self):
        self.validator = TemplateValidator()

    def _render(self, template_string):
        return Template(
            '{{% load statistics_tags %}}{}'.format(template_string)
        ).render(Context())

    def test_gets_no_kwargs(self):
        """Not valid template tag"""
        template_string = '{% num_incidents 200 %}'
        with self.assertRaises(TemplateSyntaxError):
            self._render(template_string)
        with self.assertRaises(ValidationError):
            self.validator(template_string)

    def test_gets_no_args(self):
        """Not valid template tag"""
        template_string = '{% num_incidents %}'
        self.validator(template_string)
        result = self._render(template_string)
        self.assertEqual(result, '2')

    def test_gets_valid_search(self):
        """Valid template tag with constant search param"""
        template_string = '{% num_incidents search="hello" %}'
        self.validator(template_string)
        result = self._render(template_string)
        self.assertEqual(result, '1')

    def test_gets_variable_param(self):
        """Valid template tag with missing variable search param"""
        template_string = '{% num_incidents search=hello %}'
        with self.assertRaises(ValidationError):
            self.validator(template_string)
        result = self._render(template_string)
        self.assertEqual(result, '2')

    def test_manyrelationfilter_gets_integer_id(self):
        """Valid template tag with integer id instead of string"""
        template_string = '{{% num_incidents categories={} %}}'.format(self.category.id)
        self.validator(template_string)
        result = self._render(template_string)
        self.assertEqual(result, '1')

    def test_relationfilter_gets_integer_id(self):
        """Valid template tag with integer id instead of string"""
        template_string = '{% num_incidents state=1 %}'
        self.validator(template_string)
        result = self._render(template_string)
        self.assertEqual(result, '0')

    def test_gets_invalid_dates(self):
        """Valid tag but not valid params"""
        template_string = '{% num_incidents date_lower="2018-01-01" date_upper="2017-01-01" %}'
        result = self._render(template_string)
        self.assertEqual(result, '')
        with self.assertRaises(ValidationError):
            self.validator(template_string)

    def test_gets_valid_dates(self):
        """Valid tag but not valid params"""
        template_string = '{% num_incidents date_lower="2015-06-01" date_upper="2016-06-01" %}'
        self.validator(template_string)
        result = self._render(template_string)
        self.assertEqual(result, '1')


class TestIncidentsInYearRangeByMonth(TestCase):
    """Test that incidents_in_year_range_by_month tag """
    @classmethod
    def setUpTestData(cls):
        IncidentPageFactory(date=datetime.date(2017, 1, 1))
        IncidentPageFactory(date=datetime.date(2017, 2, 1))
        IncidentPageFactory(date=datetime.date(2016, 1, 1))
        IncidentPageFactory(date=datetime.date(2015, 1, 1))

    def assert_is_map(self, obj):
        """Assert that an object is a statistics map object

        This function will raise an AssertionError if the given object
        is not a "statistical map", i.e. a list of 2-tuples or an empty
        list.

        """
        self.assertIsInstance(obj, list)
        for item in obj:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)

    def test_should_be_type_map(self):
        """should return a map."""
        incidents = incidents_in_year_range_by_month(2016, 2017)
        self.assert_is_map(incidents)
