from rest_framework.test import APITestCase
from wagtail.core.models import Site
from django.urls import reverse

from incident.models import choices
from common.tests.factories import (
    PersonPageFactory,
    CategoryPageFactory,
    CustomImageFactory,
    CommonTagFactory,
)
from incident.tests.factories import (
    IncidentPageFactory,
    IncidentIndexPageFactory,
    IncidentUpdateFactory,
    IncidentLinkFactory,
    VenueFactory,
)


class IncidentAPITest(APITestCase):
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
            # collection=photo_collection,
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

    def test_api_requests_are_successful(self):
        response = self.client.get(
            reverse('incidentpage-list'),
            HTTP_ACCEPT='application/json',
        )

        self.assertEqual(response.status_code, 200)

    def test_result_attributes(self):
        response = self.client.get(
            reverse('incidentpage-list'),
            HTTP_ACCEPT='application/json',
        )
        data = response.json()[0]
        inc = self.incident

        self.maxDiff = None
        self.assertEqual(
            data,
            {
                'title': inc.title,
                'url': inc.get_full_url(),
                'first_published_at': inc.first_published_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'last_published_at': inc.last_published_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'latest_revision_created_at': inc.latest_revision_created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'authors': [author.author.title for author in inc.authors.all()],
                'updates': [str(update) for update in inc.updates.all()],
                'categories': [cat.category.title for cat in inc.categories.all()],
                'links': [{'title': link.title, 'url': link.url, 'publication': link.publication} for link in inc.links.all()],
                'equipment_seized': [{'equipment': e.equipment.name, 'quantity': e.quantity} for e in inc.equipment_seized.all()],
                'equipment_broken': [{'equipment': e.equipment.name, 'quantity': e.quantity} for e in inc.equipment_broken.all()],
                'date': inc.date.isoformat(),
                'exact_date_unknown': inc.exact_date_unknown,
                'city': inc.city,
                'state': {'name': inc.state.name, 'abbreviation': inc.state.abbreviation},
                'teaser': str(inc.teaser),
                'body': str(inc.body),
                'teaser_image': inc.teaser_image.get_rendition('fill-1330x880').url,
                'primary_video': inc.primary_video,
                'image_caption': inc.image_caption,
                'arrest_status': inc.get_arrest_status_display(),
                'status_of_charges': inc.get_status_of_charges_display(),
                'arresting_authority': str(inc.arresting_authority),
                'release_date': inc.release_date.isoformat(),
                'detention_date': inc.detention_date.isoformat(),
                'unnecessary_use_of_force': inc.unnecessary_use_of_force,
                'lawsuit_name': inc.lawsuit_name,
                'venue': [str(e) for e in inc.venue.all()],
                'status_of_seized_equipment': inc.get_status_of_seized_equipment_display(),
                'is_search_warrant_obtained': inc.is_search_warrant_obtained,
                'actor': inc.get_actor_display(),
                'border_point': inc.border_point,
                'stopped_at_border': inc.stopped_at_border,
                'target_us_citizenship_status': inc.get_target_us_citizenship_status_display(),
                'denial_of_entry': inc.denial_of_entry,
                'stopped_previously': inc.stopped_previously,
                'target_nationality': [str(e) for e in inc.target_nationality.all()],
                'did_authorities_ask_for_device_access': inc.get_did_authorities_ask_for_device_access_display(),
                'did_authorities_ask_for_social_media_user': inc.get_did_authorities_ask_for_social_media_user_display(),
                'did_authorities_ask_for_social_media_pass': inc.get_did_authorities_ask_for_social_media_pass_display(),
                'did_authorities_ask_about_work': inc.get_did_authorities_ask_about_work_display(),
                'were_devices_searched_or_seized': inc.get_were_devices_searched_or_seized_display(),
                'assailant': inc.get_assailant_display(),
                'was_journalist_targeted': inc.get_was_journalist_targeted_display(),
                'workers_whose_communications_were_obtained': [str(w) for w in inc.workers_whose_communications_were_obtained.all()],
                'charged_under_espionage_act': inc.charged_under_espionage_act,
                'subpoena_type': inc.get_subpoena_type_display(),
                'subpoena_statuses': [dict(choices.SUBPOENA_STATUS)[status] for status in inc.subpoena_statuses],
                'held_in_contempt': inc.get_held_in_contempt_display(),
                'detention_status': inc.get_detention_status_display(),
                'third_party_in_possession_of_communications': inc.third_party_in_possession_of_communications,
                'third_party_business': inc.get_third_party_business_display(),
                'legal_order_type': inc.get_legal_order_type_display(),
                'status_of_prior_restraint': inc.get_status_of_prior_restraint_display(),
                'targeted_journalists': [e.summary for e in inc.targeted_journalists.all()],
                'targeted_institutions': [str(e) for e in inc.targeted_institutions.all()],
                'tags': [str(e) for e in inc.tags.all()],
                'current_charges': [str(e) for e in inc.current_charges.all()],
                'dropped_charges': [str(e) for e in inc.dropped_charges.all()],
                'politicians_or_public_figures_involved': [str(e) for e in inc.politicians_or_public_figures_involved.all()],

            }
        )

    def test_filtering(self):
        IncidentPageFactory(
            parent=self.incident_index,
            categories=[self.cat2],
        )
        response = self.client.get(
            reverse('incidentpage-list'),
            {'categories': str(self.cat1.pk)},
            HTTP_ACCEPT='application/json',
        )

        self.assertEqual(len(response.json()), 1)

    def test_dynamic_fields(self):
        response = self.client.get(
            reverse('incidentpage-list'),
            {'fields': 'city,state'},
            HTTP_ACCEPT='application/json',
        )

        self.assertEqual(
            list(response.json()[0].keys()),
            ['city', 'state'],
        )
