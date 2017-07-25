from django.test import TestCase, Client
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from wagtail.wagtailcore.models import Site

from .factories import IncidentIndexPageFactory, IncidentPageFactory


class IncidentCacheTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        site = Site.objects.get()
        self.index = IncidentIndexPageFactory(
            parent=site.root_page,
            slug='incidents'
        )

        self.incident_page_1 = IncidentPageFactory(
            parent=self.index,
            title='Incident 1',
            slug='incident-1',
        )
        self.incident_page_2 = IncidentPageFactory(
            parent=self.index,
            title='Incident 2',
            slug='incident-2',
        )

        self.incident_page_1.move(self.index, 'first-child')
        self.incident_page_2.move(self.index, 'last-child')

        self.cache_key_teaser_1 = make_template_fragment_key(
            'incident', [True, self.incident_page_1.pk]
        )
        self.cache_key_teaser_2 = make_template_fragment_key(
            'incident', [True, self.incident_page_2.pk]

        )
        self.cache_key_detail_1 = make_template_fragment_key(
            'incident', [False, self.incident_page_1.pk]

        )
        self.cache_key_detail_2 = make_template_fragment_key(
            'incident', [False, self.incident_page_2.pk]

        )

    def test_teaser_cache_creation(self):
        self.client.get('/incidents/')
        # Assert that both incident caches got created and are different
        self.assertIsNotNone(cache.get(self.cache_key_teaser_1))
        self.assertIsNotNone(cache.get(self.cache_key_teaser_2))
        self.assertNotEqual(
            cache.get(self.cache_key_teaser_1),
            cache.get(self.cache_key_teaser_2)
        )
