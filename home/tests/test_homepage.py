from wagtail.core.models import Site, Page
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

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
        incident_page = IncidentPageFactory(parent=self.home_page)
        post_data = {
            'slug': self.home_page.slug,
            'title': self.home_page.title,
            'recent_incidents_label': self.home_page.recent_incidents_label,
            'featured_incidents_label': self.home_page.featured_incidents_label,
            'statboxes_label': self.home_page.statboxes_label,
            'change_filters_message': self.home_page.change_filters_message,
            'blog_label': self.home_page.blog_label,
            'incidents-TOTAL_FORMS': 4,
            'incidents-INITIAL_FORMS': 4,
            'incidents-MIN_NUM_FORMS': 4,
            'incidents-MAX_NUM_FORMS': 0,
            'incidents-0-incident': incident_page.id,
            'incidents-0-id': '',
            'incidents-1-incident': incident_page.id,
            'incidents-1-id': '',
            'incidents-2-incident': incident_page.id,
            'incidents-2-id': '',
            'incidents-3-incident': incident_page.id,
            'incidents-3-id': '',
            'statboxes-TOTAL_FORMS': 0,
            'statboxes-INITIAL_FORMS': 0,
            'statboxes-MIN_NUM_FORMS': 0,
            'statboxes-MAX_NUM_FORMS': 0,
        }
        response = self.client.post(
            preview_url,
            post_data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), {'is_valid': True})

        response = self.client.get(preview_url)
        self.assertEqual(response.context['page'], self.home_page)
