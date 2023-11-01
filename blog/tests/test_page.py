import defusedxml.ElementTree as ET
import wagtail.blocks
from wagtail.models import Site, Page
from django.test import TestCase, Client

from common.tests.factories import PersonPageFactory, OrganizationPageFactory, CustomImageFactory, CategoryPageFactory
from home.tests.factories import HomePageFactory
from incident.tests.factories import IncidentPageFactory
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

        CustomImageFactory.create(
            file__width=800,
            file__height=600,
            file__color='green',
            collection__name='Photos',
        )

        cls.index = BlogIndexPageFactory(
            parent=site.root_page, slug='all-blogs')
        cls.blog_page = BlogPageFactory(
            parent=cls.index,
            slug='one',
            with_image=True,
        )
        cls.blog_page2 = BlogPageFactory(
            parent=cls.index,
            slug='two',
            with_teaser_chart=True,
        )
        cls.blog_page3 = BlogPageFactory(
            parent=cls.index,
            slug='three',
        )
        cat = CategoryPageFactory()
        IncidentPageFactory(categories=[cat])

    def setUp(self):
        self.client = Client()

    def test_get_index_should_succeed(self):
        """get index should succed."""
        response = self.client.get('/all-blogs/')
        self.assertEqual(response.status_code, 200)

    def test_get_index_feed_should_succeed(self):
        """get feed should succed."""
        response = self.client.get(self.index.url + 'feed/')
        self.assertEqual(
            response['content-type'], 'application/rss+xml; charset=utf-8'
        )
        self.assertEqual(response.status_code, 200)

    def test_rss_feed_has_correct_thumbnails(self):
        response = self.client.get(self.index.url + 'feed/')
        root = ET.fromstring(response.content)

        namespaces = {'media': 'http://search.yahoo.com/mrss/'}
        item1 = root.find(f".//item[title='{self.blog_page.title}']")
        item2 = root.find(f".//item[title='{self.blog_page2.title}']")

        self.assertIn(
            self.blog_page.teaser_graphic[0].value.get_rendition("original").url,
            getattr(
                item1.find(
                    'media:thumbnail',
                    namespaces=namespaces,
                ),
                'attrib', {})
            .get('url'),
        )

        expected_chart_thumbnail = self.blog_page2.teaser_graphic[0].value.svg_snapshot_mini_datauri()
        self.assertIn(
            expected_chart_thumbnail,
            getattr(
                item2.find(
                    'media:thumbnail',
                    namespaces=namespaces,
                ), 'attrib', {})
            .get('url')
        )

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
            page=self.blog_page,
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
            page=self.blog_page,
        )
        org = OrganizationPageFactory()
        response = self.client.get(f'/all-blogs/?organization={org.pk}')
        self.assertNotContains(response, 'Featured')

    def test_get_blog_page_contains_lead_graphic_image_attribution(self):
        image = CustomImageFactory()
        self.blog_page.lead_graphic = wagtail.blocks.StreamValue(
            stream_block=self.blog_page.lead_graphic.stream_block,
            stream_data=[('image', image)],
        )
        self.blog_page.save()
        expected_attribution = image.attribution
        response = self.client.get(self.blog_page.url)
        self.assertContains(
            response,
            f'<span class="media-attribution"> — {expected_attribution}</span>',
            html=True,
        )

    def test_get_blog_page_vertical_bar_chart_additional_js_media(self):
        response = self.client.get(self.blog_page.url)
        self.assertContains(response, 'verticalBarChart')

        # Remove the bar chart from the body and the lead graphic --
        # not sure if there's an easier way to ensure this!
        new_body = []
        for item in self.blog_page.body:
            if item.block_type == 'vertical_bar_chart':
                continue
            new_body.append((item.block_type, item.value))
        self.blog_page.body = new_body
        self.blog_page.lead_graphic = None
        self.blog_page.save()

        # We should no longer have that JS bundle in the response
        response = self.client.get(self.blog_page.url)
        self.assertNotContains(response, 'verticalBarChart')

    def test_get_blog_page_vertical_bar_chart_meta_image(self):
        self.assertEqual(
            self.blog_page2.get_meta_image(),
            self.blog_page2.teaser_graphic[0].value.png_snapshot_meta(),
        )

    def test_get_blog_page_normal_meta_image(self):
        self.assertEqual(
            self.blog_page.get_meta_image(),
            self.blog_page.teaser_graphic[0].value
        )

    def test_get_blog_page_absent_meta_image(self):
        self.assertIsNone(self.blog_page3.get_meta_image())
