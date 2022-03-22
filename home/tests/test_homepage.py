from wagtail.core.models import Site, Page
from wagtail.tests.utils.form_data import (
    nested_form_data,
    inline_formset,
)
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from blog.tests.factories import BlogPageFactory, BlogIndexPageFactory
from common.tests.factories import CommonTagFactory
from incident.tests.factories import IncidentPageFactory
from .factories import HomePageFactory


class HomePageTest(TestCase):
    """Incident Index Page """
    def setUp(self):
        Page.objects.filter(slug='home').delete()
        root_page = Page.objects.get(title='Root')
        self.home_page = HomePageFactory.build(parent=None, slug='home')
        root_page.add_child(instance=self.home_page)

        self.blog_index_page = BlogIndexPageFactory(parent=self.home_page)
        self.home_page.blog_index_page = self.blog_index_page
        self.home_page.save()

        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'site_name': 'Test site',
                'hostname': 'testserver',
                'port': '1111',
                'root_page': self.home_page,
            }
        )
        if not created:
            site.root_page = self.home_page
            site.save()

    def test_get_home_should_succeed(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['self'], self.home_page)

    def test_hides_empty_blog_section(self):
        self.home_page.featured_blog_posts = []
        self.home_page.save()

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            self.home_page.featured_blog_posts_label,
        )

    def test_hides_empty_incidents_section(self):
        self.home_page.featured_incidents = []
        self.home_page.save()

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            self.home_page.featured_incidents_label,
        )

    def test_get_home_page_should_succeed_if_no_blog_index_page(self):
        self.home_page.blog_index_page = None
        self.home_page.save()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['self'], self.home_page)

    def test_preview_home_should_succeed(self):
        user = User.objects.create_superuser(username='test', password='test', email='test@test.com')
        self.client.force_login(user)
        preview_url = reverse('wagtailadmin_pages:preview_on_edit', args=(self.home_page.id,))
        incident1, incident2 = IncidentPageFactory.create_batch(2, parent=self.home_page)
        post1, post2 = BlogPageFactory.create_batch(2, parent=self.home_page)
        tag1, tag2 = CommonTagFactory.create_batch(2)

        response = self.client.post(
            preview_url,
            nested_form_data({
                'slug': self.home_page.slug,
                'title': self.home_page.title,
                'recent_incidents_label': self.home_page.recent_incidents_label,
                'recent_incidents_more_label': self.home_page.recent_incidents_more_label,
                'recent_incidents_count': self.home_page.recent_incidents_count,
                'featured_incidents_label': self.home_page.featured_incidents_label,
                'featured_incidents_more_label': self.home_page.featured_incidents_more_label,

                'featured_blog_posts_label': self.home_page.featured_blog_posts_label,
                'featured_blog_posts_more_label': self.home_page.featured_blog_posts_more_label,
                'categories_label': self.home_page.categories_label,
                'categories_body': self.home_page.categories_body,
                'blog_index_page': str(self.home_page.blog_index_page.pk),
                'featured_incidents': inline_formset([
                    {'page': str(incident1.pk)},
                    {'page': str(incident2.pk)},
                ]),
                'featured_blog_posts': inline_formset([
                    {'page': str(post1.pk)},
                    {'page': str(post2.pk)},
                ]),
                'data_viz_tags': inline_formset([
                    {'tag': f'{{"pk":{tag1.pk},"title":"{tag1.title}"}}'},
                    {'tag': f'{{"pk":{tag2.pk},"title":"{tag2.title}"}}'},
                ]),
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), {'is_valid': True})

        response = self.client.get(preview_url)
        self.assertEqual(response.context['page'], self.home_page)
