from wagtail.models import Site, Page
from django.test import TestCase, Client

from common.tests.factories import PersonPageFactory, OrganizationPageFactory
from home.tests.factories import HomePageFactory
from blog.models import BlogIndexPageFeature
from .factories import (
    BlogIndexPageFactory,
    BlogPageFactory
)


class TestPages(TestCase):
    """Incident Index Page """
    @classmethod
    def setUpTestData(cls):
        Page.objects.filter(slug='home').delete()
        root_page = Page.objects.get(title='Root')
        cls.home_page = HomePageFactory.build(parent=None, slug='home')
        root_page.add_child(instance=cls.home_page)

        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'site_name': 'Test site',
                'hostname': 'testserver',
                'port': '1111',
                'root_page': cls.home_page,
            }
        )
        if not created:
            site.root_page = cls.home_page
            site.save()

        cls.index = BlogIndexPageFactory(
            parent=site.root_page, slug='all-blogs')
        cls.incident = BlogPageFactory(parent=cls.index, slug='one')

    def setUp(self):
        self.client = Client()

    def test_get_index_should_succeed(self):
        """get index should succed."""
        response = self.client.get('/all-blogs/')
        self.assertEqual(response.status_code, 200)

    def test_get_index_for_unknown_author_should_return_404(self):
        response = self.client.get('/all-blogs/?author=999')
        self.assertEqual(response.status_code, 404)

    def test_get_index_for_author_should_return_author_title_in_response(self):
        author = PersonPageFactory(title='A Person')
        response = self.client.get(f'/all-blogs/?author={author.pk}')
        self.assertContains(response, author.title)

    def test_get_index_for_author_should_not_contain_featured_blogs(self):
        BlogIndexPageFeature.objects.create(
            blog_index_page=self.index,
            page=self.incident,
        )
        author = PersonPageFactory()
        response = self.client.get(f'/all-blogs/?author={author.pk}')
        self.assertNotContains(response, 'Featured')

    def test_get_index_for_unknown_organization_should_return_404(self):
        response = self.client.get('/all-blogs/?organization=999')
        self.assertEqual(response.status_code, 404)

    def test_get_index_for_organization_should_return_organization_title_in_response(self):
        org = OrganizationPageFactory(title='An Organization')
        response = self.client.get(f'/all-blogs/?organization={org.pk}')
        self.assertContains(response, org.title)

    def test_get_index_for_organization_should_not_contain_featured_blogs(self):
        BlogIndexPageFeature.objects.create(
            blog_index_page=self.index,
            page=self.incident,
        )
        org = OrganizationPageFactory()
        response = self.client.get(f'/all-blogs/?organization={org.pk}')
        self.assertNotContains(response, 'Featured')
