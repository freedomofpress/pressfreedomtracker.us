from django.urls import reverse
from rest_framework.test import APITestCase
from requests.utils import parse_header_links
from wagtail.models import Site

from incident.tests.factories import (
    IncidentIndexPageFactory,
    IncidentPageFactory,
)


def humanize_links(response):
    links = parse_header_links(response['Link'])
    result = {}
    for link in links:
        result[link['rel']] = link
    return result


class IncidentListPaginationTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build()
        root_page.add_child(instance=cls.incident_index)

        # IncidentPageFactory.create_batch(30, parent=cls.incident_index)
        cls.incidents = []
        for month in range(1, 10):
            cls.incidents.append(IncidentPageFactory(date=f'2021-{month:02}-01'))

    def test_pagination_header_links_present(self):
        response1 = self.client.get(
            reverse('incidentpage-list', kwargs={'version': 'edge'}),
            {'limit': '3'},
        )
        links = humanize_links(response1)

        # First page should be the 3 most recent incidents
        self.assertEqual(
            [incident['date'] for incident in response1.json()],
            ['2021-09-01', '2021-08-01', '2021-07-01'],
        )
        self.assertIsNone(links.get('prev'))

        response2 = self.client.get(links['next']['url'])
        links2 = humanize_links(response2)

        # Second page should be the 3 middlemost incidents
        self.assertEqual(
            [incident['date'] for incident in response2.json()],
            ['2021-06-01', '2021-05-01', '2021-04-01'],
        )
        # Previous link should return the first page's data
        response_prev = self.client.get(links2['prev']['url'])
        self.assertEqual(response_prev.json(), response1.json())

        response3 = self.client.get(links2['next']['url'])
        links3 = humanize_links(response3)

        # Third and last page should be the 3 earliest incidents
        self.assertEqual(
            [incident['date'] for incident in response3.json()],
            ['2021-03-01', '2021-02-01', '2021-01-01'],
        )
        self.assertIsNone(links3.get('next'))
        # First page link should return the first page's data
        response_first = self.client.get(links3['first']['url'])
        self.assertEqual(response_first.json(), response1.json())

    def test_pagination_envelope_can_be_enabled_on_demand(self):
        response1 = self.client.get(
            reverse('incidentpage-list', kwargs={'version': 'edge'}),
            {'envelope': '1', 'limit': '3'},
        )
        response1_data = response1.json()
        # First page should be the 3 most recent incidents
        self.assertEqual(
            [incident['date'] for incident in response1_data['results']],
            ['2021-09-01', '2021-08-01', '2021-07-01'],
        )
        self.assertIsNone(response1_data.get('previous'))

        response2 = self.client.get(response1_data['next'])
        response_data = response2.json()

        # Second page should be the 3 middlemost incidents
        self.assertEqual(
            [incident['date'] for incident in response_data['results']],
            ['2021-06-01', '2021-05-01', '2021-04-01'],
        )
        response_prev = self.client.get(response_data['previous'])
        self.assertEqual(response_prev.json(), response1_data)

        response3 = self.client.get(response_data['next'])
        response_data = response3.json()

        # Third and last page should be the 3 earliest incidents
        self.assertEqual(
            [incident['date'] for incident in response_data['results']],
            ['2021-03-01', '2021-02-01', '2021-01-01'],
        )
        self.assertIsNone(response_data.get('next'))
        # First page link should return the first page's data
        response_first = self.client.get(response_data['first'])
        self.assertEqual(response_first.json(), response1.json())
