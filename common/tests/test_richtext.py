from django.test import TestCase
from wagtail.core.models import Site
from wagtail.core.templatetags.wagtailcore_tags import richtext

from home.tests.factories import HomePageFactory
from common.tests.factories import CategoryPageFactory


class RichTextCategoryPageLinksTests(TestCase):
    def setUp(self):
        self.root_page = Site.objects.get(is_default_site=True).root_page
        self.home_page = HomePageFactory.build()
        self.root_page.add_child(instance=self.home_page)

        self.category = CategoryPageFactory(
            parent=self.home_page,
            page_symbol='arrest',
        )

    def test_applies_category_specific_css_class(self):
        raw = f'<a id="{self.category.pk}" linktype="page">Prior Restraint</a>'
        rich = richtext(raw)
        self.assertIn(
            f'class="category category-{self.category.page_symbol}"',
            rich,
        )

    def test_leaves_non_category_links_unchanged(self):
        raw = f'<a id="{self.home_page.pk}" linktype="page">Home</a>'
        self.assertNotIn('category', richtext(raw))
