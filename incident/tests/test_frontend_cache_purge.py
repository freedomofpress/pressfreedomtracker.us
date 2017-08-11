from django.test import TestCase, Client
from unittest.mock import patch
from wagtail.wagtailcore.models import Site

from common.tests.factories import CategoryPageFactory
from incident.tests.factories import (
    IncidentPageFactory,
    IncidentCategorizationFactory,
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
        self.assertIn('Cache-Tag', response)

    def test_cache_tag_subpath(self):
        """
        Response from IncidentIndexPage with subpath should include
        Cache-Tag header

        """

        response = self.client.get('/incidents/?search=test')
        self.assertIn('Cache-Tag', response)

    @patch('incident.signals.purge_page_from_cache')
    def test_cache_purge_on_new_incident(self, purge_page_from_cache):
        "Should purge page cache for incident index page on incident creation"
        assert_never_called_with(purge_page_from_cache, self.index)
        IncidentPageFactory(parent=self.index)  # should trigger a cache purge on index page
        purge_page_from_cache.assert_any_call(self.index)

    @patch('incident.signals.purge_tags_from_cache')
    def test_cache_tag_purge_on_new_incident(self, purge_tags_from_cache):
        "Should purge cache tag for incident index page on incident creation"
        assert_never_called_with(
            purge_tags_from_cache,
            [self.index.get_cache_tag()]
        )
        IncidentPageFactory(parent=self.index)  # should trigger a cache purge on index page
        purge_tags_from_cache.assert_any_call([self.index.get_cache_tag()])


@patch('incident.signals.purge_page_from_cache')
class TestIncidentPageCachePurge(TestCase):
    def test_cache_purged_on_category_change(self, purge_page_from_cache):
        "Should purge cache for an incident in a category when category changes"
        category = CategoryPageFactory()
        incident = IncidentPageFactory()
        categorization = IncidentCategorizationFactory(
            incident_page=incident,
            category=category
        )
        # Not sure why, but the above doesn't commit this to the db
        # without the next line:
        categorization.save()

        # Cache purging should not have occurred yet
        assert_never_called_with(purge_page_from_cache, incident)

        category.title = "New Category Name"
        category.save()  # Should trigger purge on incident page

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
        category.save()  # Should NOT trigger purge on incident page

        assert_never_called_with(purge_page_from_cache, incident)

    def test_cache_purged_on_related_incident(self, purge_page_from_cache):
        "Should purge cache for an incident when a related incident changes"
        incident1 = IncidentPageFactory()
        incident2 = IncidentPageFactory(related_incidents=[incident1])

        incident1.title = 'New Incident Name'
        incident1.save()  # Should trigger purge on incident2

        purge_page_from_cache.assert_any_call(incident2)

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
        incident1.save()  # Should not trigger purge on incident2

        assert_never_called_with(purge_page_from_cache, incident2)

    def test_cache_purged_on_same_cat_incident(
        self,
        purge_page_from_cache
    ):
        """
        Should purge cache for an incident that is in the same category
        as a changed incident
        """
        category = CategoryPageFactory()
        incident1 = IncidentPageFactory()
        incident2 = IncidentPageFactory()
        categorization1 = IncidentCategorizationFactory(
            incident_page=incident1,
            category=category
        )
        categorization2 = IncidentCategorizationFactory(
            incident_page=incident2,
            category=category
        )
        # Not sure why, but the above doesn't commit this to the db
        # without the next lines:
        categorization1.save()
        categorization2.save()

        incident1.title = 'New Incident Title'
        incident1.save()

        purge_page_from_cache.assert_any_call(incident2)
