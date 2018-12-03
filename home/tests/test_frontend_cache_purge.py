from django.test import TestCase
from unittest.mock import patch
from wagtail.wagtailcore.models import Site

from home.tests.factories import HomePageFactory
from incident.tests.factories import IncidentPageFactory


@patch('home.signals.purge_page_from_cache')
class TestHomePageCacheInvalidation(TestCase):
    """
    To some extent this test case is just testing django's signals functionality
    which maybe is redundant--and runs counter to the "don't test your
    dependencies" rule--but I wanted to at least make sure the API call
    was being made, since I was not able to test locally with a real Cloudflare
    instance.

    For that reason, this test has also not been made comprehensive (i.e., I
    only test one signal when several are being registered).
    """

    def setUp(self):
        site = Site.objects.get()
        self.homepage = HomePageFactory(parent=site.root_page, slug='home')

    def test_cache_invalidated_on_new_incident(self, purge_page_from_cache):
        self.assertFalse(purge_page_from_cache.called)

        # should trigger a cache purge on homepage
        IncidentPageFactory().save_revision().publish()

        purge_page_from_cache.assert_called_with(self.homepage)
