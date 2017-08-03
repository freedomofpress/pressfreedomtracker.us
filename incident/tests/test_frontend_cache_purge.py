from django.test import TestCase
from unittest.mock import patch

from common.tests.factories import CategoryPageFactory
from incident.tests.factories import IncidentPageFactory, IncidentCategorizationFactory


@patch('incident.signals.purge_page_from_cache')
class TestIncidentPageCachePurge(TestCase):
    def test_cache_purged_on_category_change(self, purge_page_from_cache):
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
