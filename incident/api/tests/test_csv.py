import csv

from django.test import TestCase
from django.urls import reverse
from wagtail.core.models import Site

from common.tests.factories import (
    PersonPageFactory,
    CategoryPageFactory,
    CustomImageFactory,
    CommonTagFactory,
)
from incident.models import choices
from incident.tests.factories import (
    IncidentPageFactory,
    IncidentIndexPageFactory,
    IncidentUpdateFactory,
    IncidentLinkFactory,
    VenueFactory,
)


class MinimalIncidentCSVTestCase(TestCase):
    """Test incident API response for an incident with a minimal number of
    defined fields.

    """

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build()
        root_page.add_child(instance=cls.incident_index)

        cls.incident = IncidentPageFactory(
            parent=cls.incident_index,
            first_published_at=None,
            last_published_at=None,
            latest_revision_created_at=None,
            image_caption_text=None,
            city=None,
            state=None,
            body=None,
            teaser=None,
            teaser_image=None,
            image_caption=None,
            lawsuit_name=None,
            institution_targets=0,
        )

    def setUp(self):
        self.response = self.client.get(
            reverse('incidentpage-list'),
            {'format': 'csv'},
        )

    def test_csv_requests_are_successful(self):
        self.assertEqual(self.response.status_code, 200)

    def test_state_field_is_blank(self):
        content_lines = self.response.content.splitlines()
        reader = csv.reader(line.decode('utf-8') for line in content_lines)

        headers = next(reader)

        result = dict(zip(headers, next(reader)))
        self.assertEqual(result['state'], '')


class IncidentCSVTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build()
        root_page.add_child(instance=cls.incident_index)

        image = CustomImageFactory.create(
            file__width=800,
            file__height=600,
            file__color='green',
        )

        author1, author2, author3 = PersonPageFactory.create_batch(3, parent=root_page)
        cls.cat1, cls.cat2, cls.cat3 = CategoryPageFactory.create_batch(3, parent=root_page)

        cls.incident = IncidentPageFactory(
            parent=cls.incident_index,
            authors=[author1, author2],
            categories=[cls.cat1, cls.cat2],
            equipment_search=True,
            equipment_damage=True,
            arrest=True,
            border_stop=True,
            physical_attack=True,
            leak_case=True,
            workers_whose_communications_were_obtained=2,
            subpoena=True,
            prior_restraint=True,
            target_nationality=2,
            journalist_targets=2,
            institution_targets=2,
            venue=VenueFactory.create_batch(2),
            teaser_image=image,
            current_charges=2,
            dropped_charges=2,
            politicians_or_public_figures_involved=3,
        )
        tags = CommonTagFactory.create_batch(3)
        cls.incident.tags = tags
        cls.incident.save()
        IncidentUpdateFactory.create_batch(2, page=cls.incident)
        IncidentLinkFactory.create_batch(3, page=cls.incident)

    def test_csv_requests_are_successful(self):
        response = self.client.get(
            reverse('incidentpage-list'),
            {'format': 'csv'},
        )
        self.assertEqual(response.status_code, 200)

    def test_csv_columns_are_in_same_order_as_json_keys(self):
        json_response = self.client.get(
            reverse('incidentpage-list'),
        )
        csv_response = self.client.get(
            reverse('incidentpage-list'),
            {'format': 'csv'},
        )

        json_keys = list(json_response.json()[0].keys())
        content_lines = csv_response.content.splitlines()
        reader = csv.reader(line.decode('utf-8') for line in content_lines)
        csv_headers = next(reader)

        self.assertEqual(json_keys, csv_headers)

    def test_csv_supports_dynamic_fields(self):
        response = self.client.get(
            reverse('incidentpage-list'),
            {'fields': 'city,state', 'format': 'csv'},
        )
        content_lines = response.content.splitlines()
        reader = csv.reader(line.decode('utf-8') for line in content_lines)
        csv_headers = next(reader)
        self.assertEqual(
            csv_headers, ['city', 'state']
        )

    def test_results(self):
        response = self.client.get(
            reverse('incidentpage-list'),
            {'format': 'csv'},
        )
        content_lines = response.content.splitlines()
        reader = csv.reader(line.decode('utf-8') for line in content_lines)

        headers = next(reader)

        result = dict(zip(headers, next(reader)))

        inc = self.incident
        self.maxDiff = None
        self.assertEqual(
            result,
            {
                'title': inc.title,
                'url': inc.get_full_url(),
                'first_published_at': inc.first_published_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'last_published_at': inc.last_published_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'latest_revision_created_at': inc.latest_revision_created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'authors': ', '.join([author.author.title for author in inc.authors.all()]),
                'updates': ', '.join([str(update) for update in inc.updates.all()]),
                'categories': ', '.join([cat.category.title for cat in inc.categories.all()]),
                'links': ', '.join([str(link) for link in inc.links.all()]),
                'equipment_seized': ', '.join([e.summary for e in inc.equipment_seized.all()]),
                'equipment_broken': ', '.join([e.summary for e in inc.equipment_broken.all()]),
                'date': inc.date.isoformat(),
                'exact_date_unknown': str(inc.exact_date_unknown),
                'city': inc.city,
                'state': inc.state.abbreviation,
                'teaser': str(inc.teaser),
                'body': str(inc.body).replace('\n', ''),
                'teaser_image': inc.teaser_image.get_rendition('fill-1330x880').url,
                'primary_video': '',
                'image_caption': inc.image_caption,
                'arrest_status': inc.get_arrest_status_display(),
                'status_of_charges': inc.get_status_of_charges_display(),
                'arresting_authority': str(inc.arresting_authority),
                'release_date': inc.release_date.isoformat(),
                'detention_date': inc.detention_date.isoformat(),
                'unnecessary_use_of_force': str(inc.unnecessary_use_of_force),
                'lawsuit_name': inc.lawsuit_name,
                'venue': ', '.join([str(e) for e in inc.venue.all()]),
                'status_of_seized_equipment': inc.get_status_of_seized_equipment_display(),
                'is_search_warrant_obtained': str(inc.is_search_warrant_obtained),
                'actor': inc.get_actor_display(),
                'border_point': inc.border_point,
                'stopped_at_border': str(inc.stopped_at_border),
                'target_us_citizenship_status': inc.get_target_us_citizenship_status_display(),
                'denial_of_entry': str(inc.denial_of_entry),
                'stopped_previously': str(inc.stopped_previously),
                'target_nationality': ', '.join([str(e) for e in inc.target_nationality.all()]),
                'did_authorities_ask_for_device_access': inc.get_did_authorities_ask_for_device_access_display(),
                'did_authorities_ask_for_social_media_user': inc.get_did_authorities_ask_for_social_media_user_display(),
                'did_authorities_ask_for_social_media_pass': inc.get_did_authorities_ask_for_social_media_pass_display(),
                'did_authorities_ask_about_work': inc.get_did_authorities_ask_about_work_display(),
                'were_devices_searched_or_seized': inc.get_were_devices_searched_or_seized_display(),
                'assailant': inc.get_assailant_display(),
                'was_journalist_targeted': inc.get_was_journalist_targeted_display(),
                'workers_whose_communications_were_obtained': ', '.join([str(w) for w in inc.workers_whose_communications_were_obtained.all()]),
                'charged_under_espionage_act': str(inc.charged_under_espionage_act),
                'subpoena_type': inc.get_subpoena_type_display(),
                'subpoena_statuses': ', '.join([dict(choices.SUBPOENA_STATUS)[status] for status in inc.subpoena_statuses]),
                'held_in_contempt': inc.get_held_in_contempt_display(),
                'detention_status': inc.get_detention_status_display(),
                'third_party_in_possession_of_communications': inc.third_party_in_possession_of_communications,
                'third_party_business': inc.get_third_party_business_display(),
                'legal_order_type': inc.get_legal_order_type_display(),
                'status_of_prior_restraint': inc.get_status_of_prior_restraint_display(),
                'targeted_journalists': ', '.join([e.summary for e in inc.targeted_journalists.all()]),
                'targeted_institutions': ', '.join([str(e) for e in inc.targeted_institutions.all()]),
                'tags': ', '.join([str(e) for e in inc.tags.all()]),
                'current_charges': ', '.join([str(e) for e in inc.current_charges.all()]),
                'dropped_charges': ', '.join([str(e) for e in inc.dropped_charges.all()]),
                'politicians_or_public_figures_involved': ', '.join([str(e) for e in inc.politicians_or_public_figures_involved.all()]),
            }
        )

    def test_result_headers(self):
        response = self.client.get(
            reverse('incidentpage-list'),
            {'format': 'csv'},
        )
        content_lines = response.content.splitlines()
        reader = csv.reader(line.decode('utf-8') for line in content_lines)

        headers = next(reader)

        expected_headers = {
            'title',
            'url',
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
            'teaser',
            'body',
            'teaser_image',
            'primary_video',
            'image_caption',
            'arrest_status',
            'status_of_charges',
            'arresting_authority',
            'release_date',
            'detention_date',
            'unnecessary_use_of_force',
            'lawsuit_name',
            'venue',
            'status_of_seized_equipment',
            'is_search_warrant_obtained',
            'actor',
            'border_point',
            'stopped_at_border',
            'target_us_citizenship_status',
            'denial_of_entry',
            'stopped_previously',
            'target_nationality',
            'did_authorities_ask_for_device_access',
            'did_authorities_ask_for_social_media_user',
            'did_authorities_ask_for_social_media_pass',
            'did_authorities_ask_about_work',
            'were_devices_searched_or_seized',
            'assailant',
            'was_journalist_targeted',
            'workers_whose_communications_were_obtained',
            'charged_under_espionage_act',
            'subpoena_type',
            'subpoena_statuses',
            'held_in_contempt',
            'detention_status',
            'third_party_in_possession_of_communications',
            'third_party_business',
            'legal_order_type',
            'status_of_prior_restraint',
            'targeted_journalists',
            'targeted_institutions',
            'tags',
            'current_charges',
            'dropped_charges',
            'politicians_or_public_figures_involved',
        }

        self.assertEqual(
            set(headers), expected_headers,
        )
