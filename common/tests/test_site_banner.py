from django.test import TestCase

from wagtail.models import Page, Site

from common.models import SiteSettings
from common.tests.factories import SimplePageFactory
from home.tests.factories import HomePageFactory


class SiteBannerTest(TestCase):
    def setUp(self):
        Page.objects.filter(slug="home").delete()
        root_page = Page.objects.get(title="Root")
        self.home_page = HomePageFactory.build(parent=None, slug="home")
        root_page.add_child(instance=self.home_page)
        self.simple_page = SimplePageFactory(parent=self.home_page, slug="about")

        self.site, _ = Site.objects.update_or_create(
            is_default_site=True,
            defaults={"hostname": "testserver", "root_page": self.home_page},
        )

        self.site_settings = SiteSettings.for_site(self.site)

    def tearDown(self):
        self.site.clear_site_root_paths_cache()

    def set_banner(self, content, homepage_only=True, enabled=True):
        self.site_settings.banner_enabled = enabled
        self.site_settings.banner_content = content
        self.site_settings.homepage_only = homepage_only
        self.site_settings.save()

    def test_no_banner_without_content(self):
        self.set_banner(None, homepage_only=False)
        self.assertNotContains(self.client.get("/"), "site-banner")
        self.assertNotContains(self.client.get(self.simple_page.url), "site-banner")

    def test_no_banner_when_disabled(self):
        self.set_banner("<p>Donate</p>", homepage_only=False, enabled=False)
        self.assertNotContains(self.client.get("/"), "site-banner")
        self.assertNotContains(self.client.get(self.simple_page.url), "site-banner")

    def test_homepage_only_banner(self):
        self.set_banner(
            '<p>Support the PFT · <a href="https://freedom.press/donate/">donate</a></p>'
        )

        home_response = self.client.get("/")
        self.assertContains(home_response, 'class="site-banner"')
        self.assertContains(home_response, 'href="https://freedom.press/donate/"')
        self.assertNotContains(self.client.get(self.simple_page.url), "site-banner")

    def test_sitewide_banner(self):
        self.set_banner("<p>Donate</p>", homepage_only=False)

        self.assertContains(self.client.get("/"), 'class="site-banner"', count=1)
        self.assertContains(
            self.client.get(self.simple_page.url), 'class="site-banner"'
        )

    def test_dismissal_expiration_is_rendered(self):
        self.site_settings.banner_dismissal_expiration = 7
        self.set_banner("<p>Donate</p>", homepage_only=False)

        self.assertContains(
            self.client.get(self.simple_page.url), 'data-dismissal-days="7"'
        )
