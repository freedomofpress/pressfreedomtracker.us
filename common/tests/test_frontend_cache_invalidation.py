from django.test import TestCase, Client
from unittest.mock import patch
from wagtail.wagtailcore.models import Site

from common.tests.factories import CategoryPageFactory
from incident.tests.factories import IncidentPageFactory


class TestCategoryPageCacheInvalidation(TestCase):

    def setUp(self):
        self.client = Client()

        site = Site.objects.get()
        self.categorypage = CategoryPageFactory(parent=site.root_page, slug='category')

    def test_cache_tag_index(self):
        "Response from CategoryPage should include Cache-Tag header"
        response = self.client.get('/category/')
        self.assertIn('Cache-Tag', response)

    def test_cache_tag_subpath(self):
        """
        Response from IncidentIndexPage with subpath should include
        Cache-Tag header

        """

        response = self.client.get('/category/?search=test')
        self.assertIn('Cache-Tag', response)

    @patch('common.signals.purge_page_from_cache')
    def test_cache_invalidated_on_new_incident(self, purge_page_from_cache):
        """
        To some extent this test is just testing django's signals functionality
        which maybe is redundant--and runs counter to the "don't test your
        dependencies" rule--but I wanted to at least make sure the API call
        was being made, since I was not able to test locally with a real Cloudflare
        instance.
        """
        self.assertFalse(purge_page_from_cache.called)
        IncidentPageFactory()  # should trigger a cache purge on category page
        purge_page_from_cache.assert_called_with(self.categorypage)

    @patch('common.signals.purge_tags_from_cache')
    def test_cache_tag_purge_on_new_incident(self, purge_tags_from_cache):
        self.assertFalse(purge_tags_from_cache.called)
        IncidentPageFactory()  # should trigger a cache purge on category page
        purge_tags_from_cache.assert_called_with([
            self.categorypage.get_cache_tag()
        ])
