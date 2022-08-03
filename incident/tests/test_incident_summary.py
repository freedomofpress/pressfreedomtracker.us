import json
from urllib import parse

from django.test import TestCase
from wagtail.core.models import Site

from common.tests.factories import CategoryPageFactory
from incident.tests.factories import IncidentIndexPageFactory, IncidentPageFactory


class IncidentSummaryAPIPost(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build(slug='incidents')
        root_page.add_child(instance=cls.incident_index)

    def setUp(self):
        url = self.incident_index.get_full_url() + self.incident_index.reverse_subpage(
            'summary', args=()
        )
        self.response = self.client.post(url)

    def test_forbidden_POST(self):
        """POST requests should be forbidden"""
        self.assertEqual(self.response.status_code, 405)


class IncidentSummaryAPIGet(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build(slug='incidents')
        root_page.add_child(instance=cls.incident_index)

        category1 = CategoryPageFactory()
        category2 = CategoryPageFactory()

        IncidentPageFactory.create_batch(
            2,
            parent=cls.incident_index,
            categories=[category1],
            institution_targets=1,
            journalist_targets=1,
        )
        IncidentPageFactory.create_batch(2, categories=[category2])

        cls.category = category1

    def setUp(self):
        base_url = self.incident_index.get_full_url() + self.incident_index.reverse_subpage(
            'summary', args=()
        )
        query_string = parse.urlencode({'categories': self.category.pk})
        url = '{base}?{query_string}'.format(base=base_url, query_string=query_string)
        self.response = self.client.get(url)
        self.response_data = json.loads(self.response.content.decode('utf-8'))

    def test_response_code_success(self):
        self.assertEqual(self.response.status_code, 200)

    def test_total_incidents(self):
        self.assertEqual(self.response_data['total'], 2)

    def test_total_journalists(self):
        self.assertEqual(self.response_data['journalists'], 2)

    def test_total_institutions(self):
        self.assertEqual(self.response_data['institutions'], 4)
