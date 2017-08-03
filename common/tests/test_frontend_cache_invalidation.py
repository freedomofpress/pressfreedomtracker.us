from django.test import TestCase
from unittest.mock import patch
from wagtail.wagtailcore.models import Site

from common.tests.factories import CategoryPageFactory
from incident.tests.factories import IncidentPageFactory


@patch('common.signals.purge_page_from_cache')
class TestCategoryPageCacheInvalidation(TestCase):
    """
    To some extent this test case is just testing django's signals functionality
    which maybe is redundant--and runs counter to the "don't test your
    dependencies" rule--but I wanted to at least make sure the API call
    was being made, since I was not able to test locally with a real Cloudflare
    instance.
    """

    def setUp(self):
        site = Site.objects.get()
        self.categorypage = CategoryPageFactory(parent=site.root_page, slug='home')

    def test_cache_invalidated_on_new_incident(self, purge_page_from_cache):
        self.assertFalse(purge_page_from_cache.called)
        IncidentPageFactory()  # should trigger a cache purge on category page
        purge_page_from_cache.assert_called_with(self.categorypage)
