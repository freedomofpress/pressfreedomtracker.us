from django.test import TestCase, Client
from wagtail.wagtailcore.models import Site

from blog.tests.factories import BlogIndexPageFactory
from common.tests.factories import PersonPageFactory


class TestBlogIndexPageCachePurge(TestCase):
    def setUp(self):
        self.client = Client()

        site = Site.objects.get()
        self.index = BlogIndexPageFactory(
            parent=site.root_page, slug='blog')
        self.author = PersonPageFactory()

    def test_cache_tag_index(self):
        "Response from BlogIndexPage should include Cache-Tag header"
        response = self.client.get('/blog/')
        self.assertIn('Cache-Tag', response)

    def test_cache_tag_subpath(self):
        """
        Response from BlogIndexPage with subpath should include
        Cache-Tag header

        """

        response = self.client.get('/blog/?author={}'.format(self.author.pk))
        self.assertIn('Cache-Tag', response)
