from datetime import date
import unittest

from django.test import TestCase, RequestFactory

from common.tests.factories import CategoryPageFactory
from incident.utils.incident_filter import IncidentFilter


class FromRequestTest(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_empty_GET(self):
        request = self.factory.get('/')
        incident_filter = IncidentFilter.from_request(request)
        incident_filter.clean()
        self.assertEqual(incident_filter.cleaned_data, {})

    def test_passes_basic_values(self):
        request = self.factory.get('/', {
            'search': 'text',
            'categories': '1',
            'affiliation': 'affiliation',
            'city': 'Seattle',
            'date_lower': '2017-01-01',
            'date_upper': '2017-01-31',
            'state': '1',
            'tags': '2,3',
            'targets': '1',
        })
        incident_filter = IncidentFilter.from_request(request)
        incident_filter.clean()
        self.assertEqual(incident_filter.cleaned_data, {
            'search': 'text',
            'categories': [1],
            'affiliation': 'affiliation',
            'city': 'Seattle',
            'date': (date(2017, 1, 1), date(2017, 1, 31)),
            'state': '1',
            'tags': [2, 3],
            'targets': [1],
        })


class CategoryFiltersTest(TestCase):
    def setUp(self):
        self.category = CategoryPageFactory(title='Denial of Access')

    def test_includes_category_filters(self):
        incident_filter = IncidentFilter({
            'categories': str(self.category.id),
        })
        incident_filter.clean()
        self.assertEqual(
            {f.name for f in incident_filter.filters},
            set(IncidentFilter.base_filters) | {'politicians_or_public_figures_involved'}
        )
