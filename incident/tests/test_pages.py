from wagtail.wagtailcore.models import Site
from django.test import TestCase, Client

from .factories import IncidentIndexPageFactory


class TestPages(TestCase):
    def setUp(self):
        self.client = Client()

        site = Site.objects.get()
        self.index = IncidentIndexPageFactory(
            parent=site.root_page, slug='incidents')

    def test_get_index_should_succeed(self):
        response = self.client.get('/incidents/')
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_succeed_with_filters(self):
        response = self.client.get(
            '/incidents/?search=text&upper_date=2017-01-01&categories=1,2'
        )
        self.assertEqual(response.status_code, 200)

    def test_get_index_should_succeed_with_malformed_filters(self):
        response = self.client.get(
            '/incidents/?upper_date=aaa&lower_date=2011-54-39'
        )
        self.assertEqual(response.status_code, 200)
