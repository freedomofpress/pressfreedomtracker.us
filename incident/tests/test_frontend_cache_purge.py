from django.test import TestCase, Client
from unittest.mock import patch
from wagtail.wagtailcore.models import Site

from common.tests.factories import CategoryPageFactory
from incident.tests.factories import (
    IncidentPageFactory,
    IncidentCategorizationFactory,
    IncidentIndexPageFactory,
)


class TestIncidentIndexPageCachePurge(TestCase):
    def setUp(self):
        self.client = Client()

        site = Site.objects.get()
        self.index = IncidentIndexPageFactory(
            parent=site.root_page, slug='incidents')

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
        self.assertFalse(purge_page_from_cache.called)

        category.title = "New Category Name"
        category.save()  # Should trigger purge on incident page

        purge_page_from_cache.assert_called_with(incident)

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

        self.assertFalse(purge_page_from_cache.called)

    def test_cache_purged_on_related_incident(self, purge_page_from_cache):
        "Should purge cache for an incident when a related incident changes"
        incident1 = IncidentPageFactory()
        incident2 = IncidentPageFactory(related_incidents=[incident1])

        incident1.title = 'New Incident Name'
        incident1.save()  # Should trigger purge on incident2

        purge_page_from_cache.assert_called_with(incident2)

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
        incident1.save()  # Should trigger purge on incident2

        self.assertFalse(purge_page_from_cache.called)

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

        purge_page_from_cache.assert_called_with(incident2)
