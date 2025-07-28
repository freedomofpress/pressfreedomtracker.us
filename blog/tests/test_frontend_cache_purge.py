from unittest.mock import patch

from django.test import TestCase, Client
from wagtail.models import Site

from blog.tests.factories import BlogIndexPageFactory, BlogPageFactory
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
        self.assertEqual(response['Cache-Tag'], 'blog-index-{}'.format(self.index.pk))

    def test_cache_tag_subpath(self):
        """
        Response from BlogIndexPage with subpath should include
        Cache-Tag header

        """

        response = self.client.get('/blog/?author={}'.format(self.author.pk))
        self.assertEqual(response['Cache-Tag'], 'blog-index-{}'.format(self.index.pk))

    @patch('blog.signals.purge_page_from_cache')
    def test_cache_invalidated_on_new_incident(self, purge_page_from_cache):
        """
        BlogIndexPage should be purged from cache upon new BlogPage creation
        """
        self.assertFalse(purge_page_from_cache.called)

        # should trigger a cache purge on category page
        BlogPageFactory(parent=self.index).save_revision().publish()

        purge_page_from_cache.assert_called_with(self.index)

    @patch('blog.signals.purge_tags_from_cache')
    def test_cache_tag_purge_on_new_blog(self, purge_tags_from_cache):
        self.assertFalse(purge_tags_from_cache.called)

        # Should trigger a purge of the blog index cache tag
        BlogPageFactory(parent=self.index).save_revision().publish()

        purge_tags_from_cache.assert_called_with([self.index.get_cache_tag()])
