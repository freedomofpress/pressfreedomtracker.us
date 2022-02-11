from wagtail.core.models import Site, Page
from django.test import TestCase, Client


from home.tests.factories import HomePageFactory
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
