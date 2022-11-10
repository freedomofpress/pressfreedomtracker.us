import json

from django.test import TestCase
from wagtail.models import Site, Page

from incident.tests.factories import (
    TopicPageFactory,
    IncidentPageFactory,
    IncidentIndexPageFactory,
    TargetedJournalistFactory,
)
from common.tests.factories import CategoryPageFactory
from home.tests.factories import HomePageFactory


class TopicPageApi(TestCase):
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

        self.index = IncidentIndexPageFactory.create(
            parent=self.home_page
        )
        self.topic = TopicPageFactory(
            parent=self.home_page,
            incident_index_page=self.index,
            incidents_per_module=3,
        )

        self.cat1 = CategoryPageFactory.create(
            title='Malfeasance',
            plural_name='Malfeasances'
        )
        self.cat2 = CategoryPageFactory.create(
            title='Skullduggery',
            plural_name='Instances of Skullduggery'
        )

        self.inc1 = IncidentPageFactory.create(
            date='2020-01-01',
            categories=[self.cat1],
            tags=[self.topic.incident_tag],
            parent=self.index,
        )

        self.inc2 = IncidentPageFactory.create(
            date='2020-01-03',
            categories=[self.cat1],
            tags=[self.topic.incident_tag],
            parent=self.index,
        )

        self.inc3 = IncidentPageFactory.create(
            date='2020-01-02',
            categories=[self.cat1],
            tags=[self.topic.incident_tag],
            parent=self.index,
        )

        self.inc4 = IncidentPageFactory.create(
            date='2019-12-31',
            categories=[self.cat1],
            parent=self.index,
        )

        IncidentPageFactory.create_batch(
            6,
            date='2019-12-31',
            tags=[self.topic.incident_tag],
            categories=[self.cat2],
            parent=self.index,
        )
        self.draft_incident = IncidentPageFactory.create(
            live=False,
            date='2020-01-01',
            tags=[self.topic.incident_tag],
            categories=[self.cat2],
            parent=self.index,
        )

        # Four targeted journalists on incidents within the topic
        self.tj_incident_1 = TargetedJournalistFactory(incident=self.inc1)
        TargetedJournalistFactory.create_batch(3, incident=self.inc2)

        # One targeted journalist on an incident outside of the topic
        TargetedJournalistFactory(incident=self.inc4)

        self.url = self.topic.get_full_url() + 'incidents/'

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
        self.assertEqual(cat['symbol'], self.cat1.page_symbol)
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


class TopicPageApiWithDateRange(TestCase):
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

        self.index = IncidentIndexPageFactory.create(
            parent=self.home_page
        )
        self.topic = TopicPageFactory(
            parent=self.home_page,
            incident_index_page=self.index,
            incidents_per_module=3,
        )

        self.cat = CategoryPageFactory.create(
            title='Malfeasance',
            plural_name='Malfeasances'
        )

        self.inc1 = IncidentPageFactory.create(
            date='2021-01-01',
            categories=[self.cat],
            tags=[self.topic.incident_tag],
            parent=self.index,
        )

        self.inc2 = IncidentPageFactory.create(
            date='2021-02-01',
            categories=[self.cat],
            tags=[self.topic.incident_tag],
            parent=self.index,
        )

        self.inc3 = IncidentPageFactory.create(
            date='2021-03-01',
            categories=[self.cat],
            tags=[self.topic.incident_tag],
            parent=self.index,
        )

        self.tj_incident_1 = TargetedJournalistFactory(incident=self.inc1)
        TargetedJournalistFactory.create_batch(2, incident=self.inc2)
        TargetedJournalistFactory.create_batch(4, incident=self.inc3)

        self.url = self.topic.get_full_url() + 'incidents/'

    def test_topic_page_with_start_and_end_date_limits_incidents(self):
        self.topic.start_date = '2021-01-15'
        self.topic.end_date = '2021-02-15'
        self.topic.save()

        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))

        category_data = data[0]
        incidents = category_data['incidents']

        self.assertEqual(
            {incident['date'] for incident in incidents},
            {str(self.inc2.date)}
        )
        self.assertEqual(category_data['total_incidents'], 1)
        self.assertEqual(category_data['total_journalists'], 2)

    def test_topic_page_with_start_date_limits_incidents(self):
        self.topic.start_date = '2021-02-02'
        self.topic.end_date = None
        self.topic.save()

        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))

        category_data = data[0]
        incidents = category_data['incidents']

        self.assertEqual(
            {incident['date'] for incident in incidents},
            {str(self.inc3.date)}
        )
        self.assertEqual(category_data['total_incidents'], 1)
        self.assertEqual(category_data['total_journalists'], 4)

    def test_topic_page_with_end_date_limits_incidents(self):
        self.topic.start_date = None
        self.topic.end_date = '2021-02-01'
        self.topic.save()

        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))

        category_data = data[0]
        incidents = category_data['incidents']

        self.assertEqual(
            {incident['date'] for incident in incidents},
            {str(self.inc1.date), str(self.inc2.date)}
        )
        self.assertEqual(category_data['total_incidents'], 2)
        self.assertEqual(category_data['total_journalists'], 3)

    def test_topic_page_with_single_day_date_range(self):
        self.topic.start_date = '2021-02-01'
        self.topic.end_date = '2021-02-01'
        self.topic.save()

        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))

        incidents = data[0]['incidents']

        self.assertEqual(
            {incident['date'] for incident in incidents},
            {str(self.inc2.date)}
        )

    def test_topic_page_date_range_inexact_incident_dates(self):
        self.topic.start_date = '2021-01-15'
        self.topic.end_date = '2021-02-15'
        self.topic.save()

        incident = IncidentPageFactory.create(
            date='2021-02-20',
            exact_date_unknown=True,
            categories=[self.cat],
            tags=[self.topic.incident_tag],
            parent=self.index,
        )
        TargetedJournalistFactory.create_batch(8, incident=incident)

        response = self.client.get(self.url)
        data = json.loads(response.content.decode('utf-8'))

        category_data = data[0]
        incidents = category_data['incidents']

        self.assertEqual(
            {incident['date'] for incident in incidents},
            {str(self.inc2.date), str(incident.date)}
        )
        self.assertEqual(category_data['total_incidents'], 2)
        self.assertEqual(category_data['total_journalists'], 10)
