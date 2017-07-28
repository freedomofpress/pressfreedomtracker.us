import csv

from wagtail.wagtailcore.models import Site
from django.test import TestCase, Client

from incident.models.incident_page import IncidentPage
from incident.models.export import is_exportable, to_row
from .factories import IncidentIndexPageFactory, IncidentPageFactory


class TestPages(TestCase):
    """Incident Index Page """
    def setUp(self):
        self.client = Client()

        site = Site.objects.get()
        self.index = IncidentIndexPageFactory(
            parent=site.root_page, slug='incidents')

    def test_get_index_should_succeed(self):
        """get index should succed."""
        response = self.client.get('/incidents/')
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_succeed_with_filters(self):
        """get index with filters should succeed."""
        response = self.client.get(
            '/incidents/?search=text&date_upper=2017-01-01&categories=1,2'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_succeed_with_malformed_filters(self):
        """get index should succeed with malformed filters."""
        response = self.client.get(
            '/incidents/?date_upper=aaa&date_lower=2011-54-39'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_succeed_with_illegal_date_range(self):
        """get index should succeed with malformed filters."""
        response = self.client.get(
            '/incidents/?date_upper=2011-01-01&date_lower=2012-01-01'
        )
        self.assertEqual(response.status_code, 200)


class TestExportPage(TestCase):
    """CSV Exports"""
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

        site = Site.objects.get()
        cls.index = IncidentIndexPageFactory(
            parent=site.root_page, slug='incidents')

    def test_export_should_succeed(self):
        """request should succeed."""
        response = self.client.get(
            '/incidents/export/'
        )
        self.assertEqual(response.status_code, 200)

    def test_export_should_include_headers(self):
        """ should include headers"""
        response = self.client.get(
            '/incidents/export/'
        )
        content_lines = list(response.streaming_content)
        expected_headers = [
            field.name for field in IncidentPage._meta.get_fields()
            if is_exportable(field)
        ]
        self.assertEqual(
            content_lines[0].decode('utf-8'),
            ','.join(expected_headers) + '\r\n',
        )

    def test_export_should_include_incidents_only_live_incidents(self):
        """should include only live incidents."""
        inc = IncidentPageFactory(title='Live incident')
        IncidentPageFactory(title='Unpublished incident', live=False)
        response = self.client.get(
            '/incidents/export/'
        )

        content_lines = list(response.streaming_content)
        reader = csv.reader(line.decode('utf-8') for line in content_lines)
        next(reader)  # skip the header row
        csv_line = next(reader)
        self.assertEqual(to_row(inc), csv_line)
        for line in content_lines:
            self.assertNotIn('Unpublished incident', line.decode('utf-8'))
