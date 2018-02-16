from datetime import date
from unittest import TestCase

from django.test import RequestFactory

from incident.utils.incident_filter import IncidentFilter


class FromRequestTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_empty_GET(self):
        request = self.factory.get('/')
        incident_filter = IncidentFilter.from_request(request)
        incident_filter.clean()
        self.assertEqual(incident_filter.cleaned_data, {
            'search': None,
            'categories': None,
            'affiliation': None,
            'city': None,
            'date': None,
            'state': None,
            'tags': None,
            'targets': None,
        })

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
