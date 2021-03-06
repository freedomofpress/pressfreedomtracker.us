import json

from django.test import TestCase
from wagtail.core.models import Site, Page

from incident.tests.factories import (
    TopicPageFactory,
    IncidentPageFactory,
    IncidentIndexPageFactory,
    TargetedJournalistFactory,
)
from common.tests.factories import CategoryPageFactory
from home.tests.factories import HomePageFactory


class TopicPageApi(TestCase):
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

        cls.index = IncidentIndexPageFactory.create(
            parent=cls.home_page
        )
        cls.topic = TopicPageFactory(
            parent=cls.home_page,
            incident_index_page=cls.index,
            incidents_per_module=3,
        )

        cls.cat1 = CategoryPageFactory.create(
            title='Malfeasance',
            plural_name='Malfeasances'
        )
        cls.cat2 = CategoryPageFactory.create(
            title='Skullduggery',
            plural_name='Instances of Skullduggery'
        )

        cls.inc1 = IncidentPageFactory.create(
            date='2020-01-01',
            categories=[cls.cat1],
            tags=[cls.topic.incident_tag],
            parent=cls.index,
        )

        cls.inc2 = IncidentPageFactory.create(
            date='2020-01-03',
            categories=[cls.cat1],
            tags=[cls.topic.incident_tag],
            parent=cls.index,
        )

        cls.inc3 = IncidentPageFactory.create(
            date='2020-01-02',
            categories=[cls.cat1],
            tags=[cls.topic.incident_tag],
            parent=cls.index,
        )

        cls.inc4 = IncidentPageFactory.create(
            date='2019-12-31',
            categories=[cls.cat1],
            parent=cls.index,
        )

        IncidentPageFactory.create_batch(
            6,
            date='2019-12-31',
            tags=[cls.topic.incident_tag],
            categories=[cls.cat2],
            parent=cls.index,
        )
        cls.draft_incident = IncidentPageFactory.create(
            live=False,
            date='2020-01-01',
            tags=[cls.topic.incident_tag],
            categories=[cls.cat2],
            parent=cls.index,
        )

        # Four targeted journalists on incidents within the topic
        cls.tj_incident_1 = TargetedJournalistFactory(incident=cls.inc1)
        TargetedJournalistFactory.create_batch(3, incident=cls.inc2)

        # One targeted journalist on an incident outside of the topic
        TargetedJournalistFactory(incident=cls.inc4)

        cls.url = cls.topic.get_full_url() + 'incidents/'

    def test_GET_returns_a_200_response(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_GET_returns_json(self):
        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(data), 2)

    def test_GET_returns_sorted_json(self):
        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data[0]['category'], self.cat2.title)
        self.assertEqual(data[1]['category'], self.cat1.title)

    def test_GET_returns_correct_category_json(self):
        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))

        cat = data[1]
        self.assertEqual(cat['category'], self.cat1.title)
        self.assertEqual(cat['category_plural'], self.cat1.plural_name)
        self.assertEqual(cat['color'], self.cat1.page_color)
        self.assertEqual(cat['methodology'], self.cat1.methodology)
        self.assertEqual(cat['url'], self.cat1.get_full_url())
        self.assertEqual(cat['total_incidents'], 3)
        self.assertEqual(len(cat['incidents']), 3)
        self.assertEqual(cat['total_journalists'], 4)

    def test_GET_limits_incidents_to_incidents_per_module_amount(self):
        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))
        cat2 = data[0]

        self.assertEqual(cat2['total_incidents'], 6)
        self.assertEqual(len(cat2['incidents']), self.topic.incidents_per_module)

    def test_GET_returns_correct_incident_json(self):
        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))

        inc = data[1]['incidents'][0]
        self.assertEqual(inc['title'], self.inc2.title)
        self.assertEqual(inc['date'], str(self.inc2.date))
        self.assertEqual(inc['url'], self.inc2.get_full_url())

    def test_GET_does_not_count_journalists_on_draft_incidents(self):
        TargetedJournalistFactory(incident=self.draft_incident)

        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))
        cat2 = data[0]

        self.assertEqual(cat2['total_journalists'], 0)

    def test_GET_does_not_include_draft_incidents(self):
        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))
        cat2 = data[0]

        self.assertNotIn(
            self.draft_incident.get_full_url(),
            [i['url'] for i in cat2['incidents']]
        )

    def test_GET_counts_distinct_journalists(self):
        TargetedJournalistFactory(
            journalist=self.tj_incident_1.journalist,
            incident=self.inc3,
        )
        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))
        cat = data[1]
        self.assertEqual(cat['total_journalists'], 4)
