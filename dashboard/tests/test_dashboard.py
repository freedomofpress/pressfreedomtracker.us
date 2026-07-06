from django.urls import reverse

from wagtail import hooks
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from common.models.settings import (
    SearchSettings,
)
from dashboard.wagtail_hooks import add_shortcuts_panel
from incident.models import PrepublicationIncidentSync, PrepublicationSyncSkippedRow
from incident.tests.factories import (
    IncidentIndexPageFactory,
)


class ShortcutsPanelTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = Page.objects.get(slug="home")
        search_settings = SearchSettings.for_site(site)

        index = IncidentIndexPageFactory(parent=root_page)
        search_settings.search_page = index
        search_settings.save()

    def setUp(self):
        super().setUp()
        self.login()

    @hooks.register_temporarily("construct_homepage_panels", add_shortcuts_panel)
    def test_image_shortcut(self):
        response = self.client.get(reverse("wagtailadmin_home"))
        self.assertContains(response, "Add a new image")

    @hooks.register_temporarily("construct_homepage_panels", add_shortcuts_panel)
    def test_incident_shortcut(self):
        response = self.client.get(reverse("wagtailadmin_home"))
        self.assertContains(response, "Add a new incident")

    @hooks.register_temporarily("construct_homepage_panels", add_shortcuts_panel)
    def test_prepublication_status(self):
        PrepublicationIncidentSync.objects.create(
            successful_rows=3,
        )
        response = self.client.get(reverse("wagtailadmin_home"))
        self.assertContains(
            response, "<dt>Unconfirmed incidents synced</dt><dd>3</dd>", html=True
        )
        self.assertNotContains(response, "Rows skipped")

    @hooks.register_temporarily("construct_homepage_panels", add_shortcuts_panel)
    def test_prepublication_sync_failed_message(self):
        PrepublicationIncidentSync.objects.create(error_message="Connection failed")
        response = self.client.get(reverse("wagtailadmin_home"))
        self.assertContains(response, "Error message")
        self.assertContains(response, "Connection failed")

    @hooks.register_temporarily("construct_homepage_panels", add_shortcuts_panel)
    def test_prepublication_skipped_rows_message(self):
        sync = PrepublicationIncidentSync.objects.create()
        PrepublicationSyncSkippedRow.objects.create(
            sync=sync, number=3, reason="Invalid date Jan 13, 2010"
        )
        PrepublicationSyncSkippedRow.objects.create(
            sync=sync, number=4, reason="Invalid date Jan 14, 2010"
        )
        response = self.client.get(reverse("wagtailadmin_home"))
        self.assertContains(response, "Rows skipped: 2", html=True)
        self.assertContains(response, "Invalid date Jan 13, 2010")
        self.assertContains(response, "Invalid date Jan 14, 2010")
