from django.test import TestCase, Client
from unittest.mock import patch
from wagtail.models import Site

from common.tests.factories import CategoryPageFactory
from incident.models import IncidentCategorization
from incident.tests.factories import (
    IncidentPageFactory,
    IncidentIndexPageFactory,
)


def assert_never_called_with(magic_mock, argument):
    if argument in magic_mock.call_args_list:
        raise AssertionError(
            'Expected {} not called with {}'.format(magic_mock, argument)
        )


class TestIncidentIndexPageCachePurge(TestCase):
    def setUp(self):
        self.client = Client()

        site = Site.objects.get()
        self.index = IncidentIndexPageFactory(
            parent=site.root_page, slug='incidents')

    def tearDown(self):
        self.index.delete()

    def test_cache_tag_index(self):
        "Response from IncidentIndexPage should include Cache-Tag header"
        response = self.client.get('/incidents/')
        self.assertEqual(response['Cache-Tag'], 'incident-index-{}'.format(self.index.pk))

    def test_cache_tag_subpath(self):
        """
        Response from IncidentIndexPage with subpath should include
        Cache-Tag header

        """

        response = self.client.get('/incidents/?search=test')
        self.assertEqual(response['Cache-Tag'], 'incident-index-{}'.format(self.index.pk))

    @patch('incident.signals.purge_page_from_cache')
    def test_cache_purge_on_new_incident(self, purge_page_from_cache):
        "Should purge page cache for incident index page on incident creation"
        assert_never_called_with(purge_page_from_cache, self.index)

        # should trigger a cache purge on index page
        IncidentPageFactory(parent=self.index).save_revision().publish()

        purge_page_from_cache.assert_any_call(self.index)

    @patch('incident.signals.purge_tags_from_cache')
    def test_cache_tag_purge_on_new_incident(self, purge_tags_from_cache):
        "Should purge cache tag for incident index page on incident creation"
        assert_never_called_with(
            purge_tags_from_cache,
            [self.index.get_cache_tag()]
        )
        # should trigger a cache purge on index page
        IncidentPageFactory(parent=self.index).save_revision().publish()

        purge_tags_from_cache.assert_any_call([self.index.get_cache_tag()])


@patch('incident.signals.purge_page_from_cache')
class TestIncidentPageCachePurge(TestCase):
    def test_cache_purged_on_category_change(self, purge_page_from_cache):
        "Should purge cache for an incident in a category when category changes"
        category = CategoryPageFactory.create()
        incident = IncidentPageFactory.create()
        incident.categories = [IncidentCategorization(category=category)]
        incident.save()

        # Cache purging should not have occurred yet
        assert_never_called_with(purge_page_from_cache, incident)

        # Should trigger purge on incident page
        category.title = "New Category Name"
        category.save_revision().publish()

        purge_page_from_cache.assert_any_call(incident)

    def test_cache_not_purged_on_wrong_category_change(
        self,
        purge_page_from_cache
    ):
        """
        Should not purge cache for an incident when a category changes if the
        incident is not in that category.
        """

        category = CategoryPageFactory()
        incident = IncidentPageFactory()

        category.title = "New Category Name"

        # Should NOT trigger purge on incident page
        category.save_revision().publish()

        assert_never_called_with(purge_page_from_cache, incident)

    def test_cache_not_purged_on_unrelated_incident(
        self,
        purge_page_from_cache
    ):
        """
        Should not purge cache for an incident when another unrelated incident
        changes
        """
        incident1 = IncidentPageFactory()
        incident2 = IncidentPageFactory()

        incident1.title = 'New Incident Name'
        incident1.save_revision().publish()  # Should not trigger purge on incident2

        assert_never_called_with(purge_page_from_cache, incident2)
