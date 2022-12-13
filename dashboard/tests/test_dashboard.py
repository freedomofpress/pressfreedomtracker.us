from wagtail import hooks

from django.urls import reverse
from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page, Site

from common.models.settings import (
    SearchSettings,
)
from incident.tests.factories import (
    IncidentIndexPageFactory,
)
from dashboard.wagtail_hooks import add_shortcuts_panel


class ShortcutsPanelTest(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = Page.objects.get(slug='home')
        search_settings = SearchSettings.for_site(site)

        index = IncidentIndexPageFactory(parent=root_page)
        search_settings.search_page = index
        search_settings.save()

    def setUp(self):
        super().setUp()
        self.login()

    @hooks.register_temporarily('construct_homepage_panels', add_shortcuts_panel)
    def test_image_shortcut(self):
        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertContains(response, 'Add a new image')

    @hooks.register_temporarily('construct_homepage_panels', add_shortcuts_panel)
    def test_incident_shortcut(self):
        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertContains(response, 'Add a new incident')
