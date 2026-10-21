from django.test import TestCase


class FPFBannerTest(TestCase):
    def test_banner_renders_on_base_template_pages(self):
        response = self.client.get("/page-that-does-not-exist/")

        self.assertContains(response, 'class="fpf-banner"', status_code=404)
        self.assertContains(response, 'href="https://freedom.press/"', status_code=404)
