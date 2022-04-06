import unittest

from django.test import TestCase, Client
from unittest.mock import patch
from wagtail.core.models import Site, Page

from common.models import FooterSettings
from common.tests.factories import CategoryPageFactory
from home.tests.factories import HomePageFactory
from incident.tests.factories import IncidentPageFactory


class TestCategoryPageCacheInvalidation(TestCase):

    def setUp(self):
        self.client = Client()

        Page.objects.filter(slug='home').delete()
        root_page = Page.objects.get(title='Root')
        self.home_page = HomePageFactory.build(parent=None, slug='home')
        root_page.add_child(instance=self.home_page)

        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'site_name': 'Test site',
                'hostname': 'testserver',
                'port': '1111',
                'root_page': self.home_page,
            }
        )
        if not created:
            site.root_page = self.home_page
            site.save()

        self.categorypage = CategoryPageFactory(parent=self.home_page, slug='category')

    @unittest.skip("Skipping till templates have been added")
    def test_cache_tag_index(self):
        "Response from CategoryPage should include Cache-Tag header"
        response = self.client.get('/category/')
        self.assertEqual(response['Cache-Tag'], 'category-page-{}'.format(self.categorypage.pk))

    @unittest.skip("Skipping till templates have been added")
    def test_cache_tag_subpath(self):
        """
        Response from IncidentIndexPage with subpath should include
        Cache-Tag header

        """

        response = self.client.get('/category/?search=test')
        self.assertEqual(response['Cache-Tag'], 'category-page-{}'.format(self.categorypage.pk))

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

        # should trigger a cache purge on category page
        IncidentPageFactory().save_revision().publish()

        purge_page_from_cache.assert_called_with(self.categorypage)

    @patch('common.signals.purge_tags_from_cache')
    def test_cache_tag_purge_on_new_incident(self, purge_tags_from_cache):
        self.assertFalse(purge_tags_from_cache.called)

        # should trigger a cache purge on category page
        IncidentPageFactory().save_revision().publish()

        list_of_arguments = purge_tags_from_cache.call_args[0][0]
        self.assertIn(self.categorypage.get_cache_tag(), list_of_arguments)

    def test_should_purge_all_cache_when_settings_changed(self):
        """Changing any Setting should purge the entire zone.

        In this case we test with FooterSettings as an example, but it
        should work for any BaseSetting subclass.
        """

        site = Site.objects.get(is_default_site=True)
        footer_settings = FooterSettings.for_site(site)
        footer_settings.parter_logo_text = 'Completely new text'
        with patch('common.signals.purge_all_from_cache') as purge_mock:
            footer_settings.save()
            purge_mock.assert_called_once_with()
