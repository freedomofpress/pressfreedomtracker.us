from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from wagtail.models import Page, Site

from common.management.commands.createcategories import CATEGORIES
from common.management.commands.createqadata import (
    GENERAL_INCIDENT_FILTERS,
    INCIDENTS_PER_CATEGORY,
    TAGS,
)
from common.models import (
    CategoryPage,
    CommonTag,
    IncidentFilterSettings,
    SearchSettings,
)
from forms.models import FormPage
from home.models import HomePage
from incident.models import IncidentIndexPage, IncidentPage
from menus.models import Menu


class CreateQADataCommand(TestCase):
    def call(self):
        call_command("createqadata", stdout=StringIO())

    def test_builds_site(self):
        """Should replace the default site with a QA home page."""
        self.call()

        site = Site.objects.get(is_default_site=True)
        home = HomePage.objects.get(slug="home")
        self.assertEqual(site.root_page.specific, home)
        self.assertEqual(site.site_name, "Press Freedom Tracker (QA)")
        self.assertIn("press freedom incidents", home.about)

    def test_loads_devuser(self):
        """Should load the `test` superuser, for tests that use the admin."""
        self.call()

        user = User.objects.get(username="test")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("test"))

    def test_builds_categories(self):
        self.call()

        home = HomePage.objects.get(slug="home")
        categories = CategoryPage.objects.child_of(home)
        self.assertEqual(categories.count(), len(CATEGORIES))
        for category in categories:
            self.assertEqual(category.viz_type, "bar")

    def test_builds_incidents(self):
        self.call()

        site = Site.objects.get(is_default_site=True)
        index = IncidentIndexPage.objects.get(slug="all-incidents")
        self.assertEqual(SearchSettings.for_site(site).search_page.specific, index)

        for category in CategoryPage.objects.all():
            incidents = IncidentPage.objects.child_of(index).filter(
                categories__category=category
            )
            self.assertEqual(incidents.count(), INCIDENTS_PER_CATEGORY)

    def test_tags_incidents(self):
        """Should give every incident one of the QA tags."""
        self.call()

        for incident in IncidentPage.objects.all():
            # get() also checks there's exactly one
            self.assertIn(incident.tags.get().title, TAGS)

    def test_configures_general_incident_filters(self):
        """Should configure the sidebar's general incident filters."""
        self.call()

        site = Site.objects.get(is_default_site=True)
        settings = IncidentFilterSettings.for_site(site)
        self.assertEqual(
            [f.incident_filter for f in settings.general_incident_filters.all()],
            GENERAL_INCIDENT_FILTERS,
        )

    def test_builds_incident_form(self):
        """Should create the incident form, with required fields to fill in."""
        self.call()

        form = FormPage.objects.get(slug="submit-incident")
        self.assertTrue(form.live)
        self.assertTrue(any(field.required for field in form.get_form_fields()))

    def test_links_incident_form_from_navigation(self):
        """Should link the incident form from the header's secondary navigation."""
        self.call()

        menu = Menu.objects.get(slug="secondary-navigation")
        item = menu.menu_items.get()
        self.assertEqual(item.text, "Submit an Incident")
        self.assertEqual(item.link_page.specific, FormPage.objects.get())

    def test_idempotent(self):
        """Should not create extra data when re-run."""
        self.call()
        self.call()

        self.assertEqual(HomePage.objects.count(), 1)
        self.assertEqual(Site.objects.filter(is_default_site=True).count(), 1)
        self.assertEqual(CategoryPage.objects.count(), len(CATEGORIES))
        self.assertEqual(
            IncidentPage.objects.count(), len(CATEGORIES) * INCIDENTS_PER_CATEGORY
        )
        self.assertEqual(CommonTag.objects.filter(title__in=TAGS).count(), len(TAGS))
        self.assertEqual(FormPage.objects.count(), 1)
        self.assertEqual(Menu.objects.filter(slug="secondary-navigation").count(), 1)

    def test_creates_root(self):
        Site.objects.all().delete()
        Page.objects.all().delete()

        self.call()

        home = HomePage.objects.get(slug="home")
        self.assertEqual(home.get_parent().depth, 1)
