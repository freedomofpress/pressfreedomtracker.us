from django.test import TestCase
from wagtail.models import Site

from incident.api.serializers import CategorySerializer
from common.tests.factories import CategoryPageFactory


class CategorySerializerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.category = CategoryPageFactory(parent=site.root_page)

    def test_successfully_serializes_category_page_urls(self):
        result = CategorySerializer(self.category)
        self.assertEqual(
            self.category.get_full_url(),
            result.data['url']
        )

    def test_resolves_methodology_links_in_html(self):
        category_with_link = CategoryPageFactory(
            parent=self.category.get_parent(),
            methodology=f"""Click <a id="{self.category.pk}" linktype="page">here</a>."""
        )
        result = CategorySerializer(category_with_link)
        self.assertIn(
            self.category.url,
            result.data['methodology'],
        )
