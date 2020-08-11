from wagtail.core.models import Site, Page
from wagtail.tests.utils.form_data import (
    nested_form_data,
    inline_formset,
    streamfield,
    rich_text,
)
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from blog.tests.factories import BlogPageFactory
from incident.tests.factories import IncidentPageFactory
from .factories import HomePageFactory


class HomePageTest(TestCase):
    """Incident Index Page """
    def setUp(self):
        Page.objects.filter(slug='home').delete()
        root_page = Page.objects.get(title='Root')
        self.home_page = HomePageFactory.build(parent=None, slug='home')
        root_page.add_child(instance=self.home_page)

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

    def test_preview_home_should_succeed(self):
        user = User.objects.create_superuser(username='test', password='test', email='test@test.com')
        self.client.force_login(user)
        preview_url = reverse('wagtailadmin_pages:preview_on_edit', args=(self.home_page.id,))
        incident1, incident2 = IncidentPageFactory.create_batch(2, parent=self.home_page)
        post1, post2 = BlogPageFactory.create_batch(2, parent=self.home_page)

        response = self.client.post(
            preview_url,
            nested_form_data({
                'slug': self.home_page.slug,
                'title': self.home_page.title,
                'recent_incidents_label': self.home_page.recent_incidents_label,
                'featured_pages_label': self.home_page.featured_pages_label,
                'statboxes_label': self.home_page.statboxes_label,
                'change_filters_message': self.home_page.change_filters_message,
                'blog_label': self.home_page.blog_label,
                'features': inline_formset([
                    {'page': str(incident1.pk)},
                    {'page': str(post1.pk)},
                    {'page': str(incident2.pk)},
                    {'page': str(post2.pk)},
                ]),
                'content': streamfield([
                    ('heading_2', nested_form_data({'content': 'What is a Vampire?'})),
                    ('raw_html', '<figure><img src="/media/example.jpg"><figcaption>A vampire at sunset</figcaption></figure>'),
                    ('rich_text', rich_text('<p><i>Lorem ipsum</i></p>')),
                ]),
                'statboxes': inline_formset([
                    {'value': '{% num_incidents categories=9 %}',
                     'label': 'Hello world',
                     'color': 'gamboge'}
                ]),
            })
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), {'is_valid': True})

        response = self.client.get(preview_url)
        self.assertEqual(response.context['page'], self.home_page)
