from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from wagtail.models import Page, Site

from home.models import HomePage


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

    def test_idempotent(self):
        """Should not create extra data when re-run."""
        self.call()
        self.call()

        self.assertEqual(HomePage.objects.count(), 1)
        self.assertEqual(Site.objects.filter(is_default_site=True).count(), 1)

    def test_creates_root(self):
        """Should create a root page on an empty page tree."""
        Site.objects.all().delete()
        Page.objects.all().delete()

        self.call()

        home = HomePage.objects.get(slug="home")
        self.assertEqual(home.get_parent().depth, 1)
