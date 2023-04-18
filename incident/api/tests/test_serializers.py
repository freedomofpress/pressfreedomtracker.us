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
