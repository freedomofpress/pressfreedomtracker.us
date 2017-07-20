from django.test import TestCase

from blog.tests.factories import BlogPageFactory, BlogIndexPageFactory
from blog.utils import BlogFilter
from blog.models import BlogPage


class TestFiltering(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.index = BlogIndexPageFactory()
        cls.post1 = BlogPageFactory()
        cls.post2 = BlogPageFactory()

    def test_should_parse_query_string_objects(self):
        """BlogFilter should parse dict-like querystring objects"""
        get_query = {
            'author': '1',
            'organization': '2',
        }
        filters = BlogFilter.from_querystring(get_query)
        self.assertEqual(filters.author, 1)
        self.assertEqual(filters.organization, 2)

    def test_should_ignore_absent_data(self):
        """BlogFilter should set absent filter values to None"""
        get_query = {
            'author': '1',
        }
        filters = BlogFilter.from_querystring(get_query)
        self.assertIsNone(filters.organization)

    def test_should_ignore_unparsable_data(self):
        """BlogFilter should set invalid data to None"""
        get_query = {
            'author': 'AAA',
        }
        filters = BlogFilter.from_querystring(get_query)
        self.assertIsNone(filters.author)

    def test_should_filter_blog_pages_by_author(self):
        """BlogFilter should filter BlogPages by author"""
        filters = BlogFilter(organization=None, author=self.post1.author.pk)
        found = filters.filter(BlogPage.objects)
        self.assertEqual(set(found), {self.post1})

    def test_should_filter_blog_pages_by_organization(self):
        """BlogFilter should filter BlogPages by organization"""
        filters = BlogFilter(organization=self.post2.organization, author=None)
        found = filters.filter(BlogPage.objects)
        self.assertEqual(set(found), {self.post2})
