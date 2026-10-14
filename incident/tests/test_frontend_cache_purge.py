from unittest.mock import patch
from urllib.parse import urljoin

from django.test import Client, TestCase
from django.urls import reverse

from wagtail.models import Site

from common.tests.factories import CategoryPageFactory
from home.tests.factories import HomePageFactory
from incident.models import IncidentCategorization, PrepublicationSettings
from incident.tests.factories import (
    IncidentIndexPageFactory,
    IncidentPageFactory,
)


def assert_never_called_with(magic_mock, argument):
    if argument in magic_mock.call_args_list:
        raise AssertionError(f"Expected {magic_mock} not called with {argument}")


class TestIncidentIndexPageCachePurge(TestCase):
    def setUp(self):
        self.client = Client()

        site = Site.objects.get()
        self.index = IncidentIndexPageFactory(parent=site.root_page, slug="incidents")

    def tearDown(self):
        self.index.delete()

    def test_cache_tag_index(self):
        "Response from IncidentIndexPage should include Cache-Tag header"
        response = self.client.get("/incidents/")
        self.assertEqual(response["Cache-Tag"], f"incident-index-{self.index.pk}")

    def test_cache_tag_subpath(self):
        """
        Response from IncidentIndexPage with subpath should include
        Cache-Tag header

        """

        response = self.client.get("/incidents/?search=test")
        self.assertEqual(response["Cache-Tag"], f"incident-index-{self.index.pk}")

    @patch("incident.signals.PurgeBatch")
    def test_cache_purge_on_new_incident(self, purge_batch_cls):
        "Should purge page cache for incident index page on incident creation"
        batch = purge_batch_cls.return_value
        assert_never_called_with(batch.add_page, self.index)

        # should trigger a cache purge on index page
        IncidentPageFactory(parent=self.index).save_revision().publish()

        batch.add_page.assert_any_call(self.index)
        batch.purge.assert_called()

    @patch("incident.signals.purge_tags_from_cache")
    def test_cache_tag_purge_on_new_incident(self, purge_tags_from_cache):
        "Should purge cache tag for incident index page on incident creation"
        assert_never_called_with(purge_tags_from_cache, [self.index.get_cache_tag()])
        # should trigger a cache purge on index page
        IncidentPageFactory(parent=self.index).save_revision().publish()

        purge_tags_from_cache.assert_any_call([self.index.get_cache_tag()])


@patch("incident.signals.PurgeBatch")
class TestIncidentPageCachePurge(TestCase):
    def test_cache_purged_on_category_change(self, purge_batch_cls):
        "Should purge cache for an incident in a category when category changes"
        category = CategoryPageFactory.create()
        incident = IncidentPageFactory.create()
        incident.categories = [IncidentCategorization(category=category)]
        incident.save()

        # Cache purging should not have occurred yet
        assert_never_called_with(purge_batch_cls.return_value.add_page, incident)

        # Should trigger purge on incident page
        category.title = "New Category Name"
        category.save_revision().publish()

        batch = purge_batch_cls.return_value
        batch.add_page.assert_any_call(incident)
        batch.purge.assert_called()

    def test_cache_not_purged_on_wrong_category_change(self, purge_batch_cls):
        """
        Should not purge cache for an incident when a category changes if the
        incident is not in that category.
        """

        category = CategoryPageFactory()
        incident = IncidentPageFactory()

        category.title = "New Category Name"

        # Should NOT trigger purge on incident page
        category.save_revision().publish()

        assert_never_called_with(purge_batch_cls.return_value.add_page, incident)

    def test_cache_not_purged_on_unrelated_incident(self, purge_batch_cls):
        """
        Should not purge cache for an incident when another unrelated incident
        changes
        """
        incident1 = IncidentPageFactory()
        incident2 = IncidentPageFactory()

        incident1.title = "New Incident Name"
        incident1.save_revision().publish()  # Should not trigger purge on incident2

        assert_never_called_with(purge_batch_cls.return_value.add_page, incident2)


@patch("incident.signals.PurgeBatch")
@patch("incident.signals.purge_urls_from_cache")
class TestPrepublicationSettingsCachePurge(TestCase):
    def setUp(self):
        self.prepub_list_url = urljoin(
            Site.objects.get().root_url, reverse("prepub_list")
        )
        self.home_page = HomePageFactory()

    def test_cache_purged_when_feature_enabled(
        self, purge_urls_from_cache, purge_batch_cls
    ):
        "Should purge the unconfirmed incidents URL when the feature is enabled"
        PrepublicationSettings.objects.create(is_enabled=True)

        purge_urls_from_cache.assert_called_once_with([self.prepub_list_url])
        batch = purge_batch_cls.return_value
        batch.add_pages.assert_called_once()
        self.assertEqual(list(batch.add_pages.call_args.args[0]), [self.home_page])
        batch.purge.assert_called_once()

    def test_cache_purged_when_feature_toggled(
        self, purge_urls_from_cache, purge_batch_cls
    ):
        "Should purge the unconfirmed incidents when the feature is toggled"
        prepub_settings = PrepublicationSettings.objects.create()
        self.assertFalse(purge_urls_from_cache.called)

        prepub_settings.is_enabled = True
        prepub_settings.save()
        purge_urls_from_cache.assert_called_once_with([self.prepub_list_url])
        batch = purge_batch_cls.return_value
        batch.add_pages.assert_called_once()
        self.assertEqual(list(batch.add_pages.call_args.args[0]), [self.home_page])
        batch.purge.assert_called_once()
