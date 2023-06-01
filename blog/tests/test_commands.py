from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from wagtail.models import Site

from ..models import BlogPage
from .factories import (
    BlogIndexPageFactory,
    BlogPageFactory
)


class ConvertBlogTypeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        s = Site.objects.get(is_default_site=True)

        index = BlogIndexPageFactory(parent=s.root_page)
        cls.blog_post = BlogPageFactory(
            title='Blog Post 1',
            blog_type=BlogPage.DEFAULT,
            parent=index,
        )
        cls.newsletter_post = BlogPageFactory(
            title='Newsletter 1',
            blog_type=BlogPage.DEFAULT,
            parent=index,
        )
        cls.special_post = BlogPageFactory(
            title='Something very special',
            blog_type=BlogPage.SPECIAL,
            parent=index,
        )

    def test_output_if_no_pages_match_selection(self):
        out = StringIO()
        call_command('convert_blog_type', '^XYZ$', 'newsletter', stdout=out)
        expected_output = "Blog page titles matching '^XYZ$': 0"
        self.assertIn(expected_output, out.getvalue())

    def test_output_if_pages_match_selection(self):
        out = StringIO()
        call_command('convert_blog_type', '^Blog', 'newsletter', stdout=out)

        self.assertIn(self.blog_post.title, out.getvalue())

    def test_updates_blog_page_type_when_commit_option_given(self):
        out = StringIO()
        call_command('convert_blog_type', '^News', 'newsletter', commit=True, stdout=out)

        self.newsletter_post.refresh_from_db()
        self.blog_post.refresh_from_db()
        self.special_post.refresh_from_db()

        self.assertEqual(self.newsletter_post.blog_type, BlogPage.NEWSLETTER)
        self.assertEqual(self.special_post.blog_type, BlogPage.SPECIAL)
        self.assertEqual(self.blog_post.blog_type, BlogPage.DEFAULT)
