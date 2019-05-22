from django.test import TestCase
from wagtail.core.models import Site

from incident.tests.factories import IncidentIndexPageFactory


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

        content = b''.join(list(response.streaming_content))

        # Since we have no incidents in the db right now, this should just be
        # a CSV header row
        self.assertEqual(content, b'title,slug,first_published_at,last_published_at,latest_revision_created_at,updates,categories,links,equipment_seized,equipment_broken,date,exact_date_unknown,affiliation,city,state,body,teaser,teaser_image,image_caption,arrest_status,status_of_charges,release_date,detention_date,unnecessary_use_of_force,lawsuit_name,status_of_seized_equipment,is_search_warrant_obtained,actor,border_point,stopped_at_border,target_us_citizenship_status,denial_of_entry,stopped_previously,did_authorities_ask_for_device_access,did_authorities_ask_for_social_media_user,did_authorities_ask_for_social_media_pass,did_authorities_ask_about_work,were_devices_searched_or_seized,assailant,was_journalist_targeted,charged_under_espionage_act,subpoena_type,subpoena_status,held_in_contempt,detention_status,third_party_in_possession_of_communications,third_party_business,legal_order_type,status_of_prior_restraint,targets,tags,current_charges,dropped_charges,venue,target_nationality,targets_whose_communications_were_obtained,politicians_or_public_figures_involved\r\n')
