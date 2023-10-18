import json

from django.test import TestCase
from wagtail.models import Site

from incident.tests.factories import IncidentIndexPageFactory, IncidentPageFactory


class IncidentExportTestCase(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        self.incident_index = IncidentIndexPageFactory.build(slug='incidents')
        root_page.add_child(instance=self.incident_index)

    def test_forbidden_POST(self):
        "POST requests should be forbidden"
        response = self.client.post(
            self.incident_index.get_full_url() + 'export/'
        )
        self.assertEqual(response.status_code, 405)

    def test_OPTIONS(self):
        """
        OPTIONS requests should be allowed and have correct headers but have
        no content
        """

        response = self.client.options(
            self.incident_index.get_full_url() + 'export/'
        )
        self.assertEqual(
            response['Access-Control-Allow-Origin'], '*'
        )
        self.assertEqual(
            response['Access-Control-ALlow-Methods'], 'GET,OPTIONS,HEAD'
        )
        self.assertEqual(response.content, b'')

    def test_GET(self):
        """
        OPTIONS requests should be allowed and have correct headers and content
        """

        response = self.client.get(
            self.incident_index.get_full_url() + 'export/'
        )
        self.assertEqual(
            response['Access-Control-Allow-Origin'], '*'
        )
        self.assertEqual(
            response['Access-Control-ALlow-Methods'], 'GET,OPTIONS,HEAD'
        )

        content = b''.join(list(response.streaming_content)).strip().decode('utf-8')

        # Since we have no incidents in the db right now, this should just be
        # a CSV header row
        headers = set(content.split(','))
        expected_headers = {
            'title',
            'slug',
            'first_published_at',
            'last_published_at',
            'latest_revision_created_at',
            'authors',
            'updates',
            'categories',
            'links',
            'equipment_seized',
            'equipment_broken',
            'date',
            'exact_date_unknown',
            'city',
            'state',
            'body',
            'introduction',
            'teaser',
            'teaser_image',
            'primary_video',
            'image_caption',
            'arrest_status',
            'arresting_authority',
            'release_date',
            'detention_date',
            'unnecessary_use_of_force',
            'case_number',
            'case_type',
            'case_statuses',
            'status_of_seized_equipment',
            'is_search_warrant_obtained',
            'actor',
            'border_point',
            'target_us_citizenship_status',
            'denial_of_entry',
            'stopped_previously',
            'did_authorities_ask_for_device_access',
            'did_authorities_ask_for_social_media_user',
            'did_authorities_ask_for_social_media_pass',
            'did_authorities_ask_about_work',
            'were_devices_searched_or_seized',
            'assailant',
            'was_journalist_targeted',
            'charged_under_espionage_act',
            'subpoena_type',
            'subpoena_statuses',
            'name_of_business',
            'third_party_business',
            'legal_order_type',
            'status_of_prior_restraint',
            'targeted_journalists',
            'targeted_institutions',
            'tags',
            'charges',
            'target_nationality',
            'workers_whose_communications_were_obtained',
            'politicians_or_public_figures_involved',
            'longitude',
            'latitude',
            'legal_orders',
            'legal_order_target',
            'legal_order_venue',
        }
        self.assertEqual(headers, expected_headers)

        # Create incidents
        IncidentPageFactory()
        response = self.client.get(
            self.incident_index.get_full_url() + 'export/?format=json'
        )
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0].keys(), expected_headers)

    def test_fields__json(self):
        IncidentPageFactory(
            city='Albuquerque',
            date='2010-01-01',
            title='Took a Wrong Turn',
        )
        response = self.client.get(
            self.incident_index.get_full_url() + 'export/?format=json&fields=title,city,date'
        )
        response_data = json.loads(response.content.decode('utf-8'))

        self.assertEqual(
            response_data,
            [{'city': 'Albuquerque', 'date': '2010-01-01', 'title': 'Took a Wrong Turn'}]
        )

    def test_fields__csv(self):
        IncidentPageFactory(
            city='Albuquerque',
            date='2010-01-01',
            title='Took a Wrong Turn',
        )
        response = self.client.get(
            self.incident_index.get_full_url() + 'export/?format=csv&fields=title,city,date'
        )

        content = b''.join(list(response.streaming_content)).strip().decode('utf-8').splitlines()
        headers = content[0].split(',')
        data = content[1].split(',')

        expected_headers = ['title', 'date', 'city']
        self.assertEqual(headers, expected_headers)

        expected_data = ['Took a Wrong Turn', '2010-01-01', 'Albuquerque']
        self.assertEqual(data, expected_data)
