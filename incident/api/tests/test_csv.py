import csv
from urllib import parse

from django.test import TestCase
from django.urls import reverse
from wagtail.models import Site

from common.tests.factories import (
    PersonPageFactory,
    CategoryPageFactory,
    CustomImageFactory,
    CommonTagFactory,
)
from incident.models import choices, IncidentPage
from incident.tests.factories import (
    IncidentPageFactory,
    IncidentIndexPageFactory,
    IncidentUpdateFactory,
    IncidentLinkFactory,
    StateFactory,
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
            introduction=None,
            teaser=None,
            teaser_image=None,
            image_caption=None,
            institution_targets=0,
        )

    def setUp(self):
        self.response = self.client.get(
            reverse('incidentpage-list', kwargs={'version': 'edge'}),
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


class PerformantCSVTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build(
            slug='incident-index',
        )
        root_page.add_child(instance=cls.incident_index)

        cls.state = StateFactory(abbreviation='NM')
        cls.cats = CategoryPageFactory.create_batch(3, parent=root_page)
        cls.tags = CommonTagFactory.create_batch(3)
        cls.incident = IncidentPageFactory(
            arrest=True,
            parent=cls.incident_index,
            categories=cls.cats,
            tags=cls.tags,
            state=cls.state,
            status_of_seized_equipment=choices.STATUS_OF_SEIZED_EQUIPMENT[0][0],
            arresting_authority__title='Police Squad!',
        )
        IncidentPageFactory()

    def setUp(self):
        fields = [
            'title',
            'tags',
            'url',
            'categories',
            'status_of_seized_equipment',
            'arresting_authority',
        ]
        url = reverse(
            'incidentpage-list',
            kwargs={'version': 'edge'},
        ) + '?' + parse.urlencode({'fields': ','.join(fields)})

        with self.assertNumQueries(3):
            self.response = self.client.get(
                url,
                HTTP_ACCEPT='text/csv',
            )
        content_lines = self.response.content.splitlines()
        reader = csv.reader(line.decode('utf-8') for line in content_lines)

        self.headers = next(reader)
        self.result = dict(zip(self.headers, next(reader)))

    def test_requests_are_successful(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_has_correct_path(self):
        self.assertTrue(
            self.result['url'].endswith(
                f'/{self.incident_index.slug}/{self.incident.slug}/'
            ),
        )

    def test_tags_are_correct(self):
        self.assertEqual(
            self.result['tags'],
            ', '.join(tag.title for tag in self.incident.tags.all())
        )

    def test_categories_are_correct(self):
        self.assertEqual(
            self.result['categories'],
            ', '.join(
                categorization.category.title for categorization in self.incident.categories.all()
            )
        )

    def test_choice_field_is_correct(self):
        self.assertEqual(
            self.result['status_of_seized_equipment'],
            self.incident.get_status_of_seized_equipment_display(),
        )

    def test_arresting_authority_is_correct(self):
        self.assertEqual(
            self.result['arresting_authority'],
            'Police Squad!',
        )


class HomePageCSVTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build()
        root_page.add_child(instance=cls.incident_index)

        cls.state = StateFactory(abbreviation='NM')
        cls.cats = CategoryPageFactory.create_batch(3, parent=root_page)
        cls.tags = CommonTagFactory.create_batch(3)
        cls.incident = IncidentPageFactory(
            parent=cls.incident_index,
            categories=cls.cats,
            tags=cls.tags,
            state=cls.state,
        )

    def setUp(self):
        self.response = self.client.get(
            reverse(
                'incidentpage-homepage_csv',
                kwargs={'version': 'edge'},
            ),
            HTTP_ACCEPT='text/csv',
        )
        content_lines = self.response.content.splitlines()
        reader = csv.reader(line.decode('utf-8') for line in content_lines)

        self.headers = next(reader)
        self.result = dict(zip(self.headers, next(reader)))

    def test_requests_are_successful(self):
        self.assertEqual(self.response.status_code, 200)

    def test_supplies_correct_headers(self):
        self.assertEqual(self.headers, [
            'date',
            'city',
            'state',
            'latitude',
            'longitude',
            'categories',
            'tags',
        ])

    def test_returns_state_abbreviation(self):
        self.assertEqual(self.result['state'], self.state.abbreviation)

    def test_returns_correct_categories_list(self):
        self.assertEqual(
            self.result['categories'],
            ', '.join(
                sorted([cat.title for cat in self.cats])
            )
        )

    def test_returns_correct_tags_list(self):
        self.assertEqual(
            self.result['tags'],
            ', '.join(
                sorted([tag.title for tag in self.tags])
            )
        )


class FilteredHomePageCSVTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build()
        root_page.add_child(instance=cls.incident_index)

        cls.state = StateFactory(abbreviation='NM')
        cls.cats = CategoryPageFactory.create_batch(3, parent=root_page)
        cls.tags = CommonTagFactory.create_batch(3)
        cls.incident1 = IncidentPageFactory(
            parent=cls.incident_index,
            categories=cls.cats,
            date='2022-01-01',
            tags=cls.tags,
            state=cls.state,
        )
        cls.incident2 = IncidentPageFactory(
            parent=cls.incident_index,
            categories=cls.cats,
            date='2022-02-02',
            tags=cls.tags,
            state=cls.state,
        )
        cls.incident3 = IncidentPageFactory(
            parent=cls.incident_index,
            categories=cls.cats,
            date='2022-03-03',
            tags=cls.tags,
            state=cls.state,
        )

    def setUp(self):
        self.response = self.client.get(
            reverse(
                'incidentpage-homepage_csv',
                kwargs={'version': 'edge'},
            ),
            {
                'date_lower': '2022-01-15',
                'date_upper': '2022-02-15',
            },
            HTTP_ACCEPT='text/csv',
        )
        content_lines = self.response.content.splitlines()
        reader = csv.reader(line.decode('utf-8') for line in content_lines)

        self.headers = next(reader)
        self.results = []
        for result in reader:
            self.results.append(dict(zip(self.headers, result)))

    def test_applies_date_filter(self):
        self.assertEqual(len(self.results), 1)
        self.assertEqual(self.results[0]['date'], '2022-02-02')


class InvalidFilterHomePageCSVTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build()
        root_page.add_child(instance=cls.incident_index)

    def setUp(self):
        self.url = reverse(
            'incidentpage-homepage_csv',
            kwargs={'version': 'edge'},
        )

    def test_returns_400_if_lower_date_argument_is_not_valid(self):
        self.response = self.client.get(
            self.url,
            {
                'date_lower': 'INVALID_DATE',
            },
            HTTP_ACCEPT='text/csv',
        )
        self.assertEqual(self.response.status_code, 400)

    def test_returns_400_if_upper_date_argument_is_not_valid(self):
        self.response = self.client.get(
            self.url,
            {
                'date_upper': 'INVALID_DATE',
            },
            HTTP_ACCEPT='text/csv',
        )
        self.assertEqual(self.response.status_code, 400)

    def test_returns_400_if_both__date_arguments_are_not_valid(self):
        self.response = self.client.get(
            self.url,
            {
                'date_lower': 'INVALID_DATE',
                'date_upper': 'INVALID_DATE',
            },
            HTTP_ACCEPT='text/csv',
        )
        self.assertEqual(self.response.status_code, 400)


class FilteredPerformantCSVTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        cls.incident_index = IncidentIndexPageFactory.build(
            slug='incident-index',
        )
        root_page.add_child(instance=cls.incident_index)

        cls.state = StateFactory(abbreviation='NM')
        cls.cats = CategoryPageFactory.create_batch(3, parent=root_page)
        cls.tags = CommonTagFactory.create_batch(3)
        cls.incident1 = IncidentPageFactory(
            parent=cls.incident_index,
            date='2022-01-01',
            categories=[cls.cats[0]],
            tags=[cls.tags[0]],
            state__abbreviation='NM',
        )
        cls.incident2 = IncidentPageFactory(
            parent=cls.incident_index,
            date='2022-02-02',
            categories=[cls.cats[1]],
            tags=[cls.tags[1]],
            state__abbreviation='AK',
        )
        cls.incident3 = IncidentPageFactory(
            parent=cls.incident_index,
            date='2022-03-03',
            categories=[cls.cats[2]],
            tags=[cls.tags[2]],
            state__abbreviation='VT',
        )

    def filtered_request(self, filters):
        fields = [
            'title',
            'date',
            'tags',
            'categories',
        ]
        response = self.client.get(
            path=reverse(
                'incidentpage-list',
                kwargs={'version': 'edge'},
            ),
            data={
                'fields': ','.join(fields),
                **filters
            },
            HTTP_ACCEPT='text/csv',
        )
        content_lines = response.content.splitlines()
        reader = csv.reader(line.decode('utf-8') for line in content_lines)

        headers = next(reader)
        result = [dict(zip(headers, row)) for row in reader]
        return result

    def test_date_filter(self):
        # 2 queries expected:
        # * 1 for the general incident filters
        # * 1 for the category incident filters
        # * 1 for the actual incident query
        with self.assertNumQueries(3):
            result = self.filtered_request({
                'date_lower': '2022-01-15',
                'date_upper': '2022-02-15',
            })
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], self.incident2.title)

    def test_tags_filter(self):
        # 2 queries expected:
        # * 1 for the general incident filters
        # * 1 for the category incident filters
        # * 1 for the actual incident query
        with self.assertNumQueries(3):
            result = self.filtered_request({
                'tags': self.tags[1].pk
            })
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], self.incident2.title)

    def test_categories_filter(self):
        # 3 queries expected:
        # * 1 for the general incident filters
        # * 1 for the category incident filters
        # * 1 for the actual incident query
        with self.assertNumQueries(3):
            result = self.filtered_request({
                'categories': self.cats[1].pk
            })
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], self.incident2.title)


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
        state = StateFactory()

        cls.incident = IncidentPageFactory(
            parent=cls.incident_index,
            authors=[author1, author2],
            categories=[cls.cat1, cls.cat2],
            city='City A',
            state=state,
            introduction='Introduction',
            teaser='Teaser',
            image_caption='Caption',
            case_number='CASENUMBER',
            case_type='CIVIL',
            equipment_search=True,
            equipment_damage=True,
            arrest=True,
            border_stop=True,
            assault=True,
            leak_case=True,
            workers_whose_communications_were_obtained=2,
            subpoena=True,
            prior_restraint=True,
            target_nationality=2,
            journalist_targets=2,
            institution_targets=2,
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
            reverse('incidentpage-list', kwargs={'version': 'edge'}),
            {'format': 'csv'},
        )
        self.assertEqual(response.status_code, 200)

    def test_csv_data_is_not_paginated(self):
        IncidentPageFactory.create_batch(30)
        response = self.client.get(
            reverse('incidentpage-list', kwargs={'version': 'edge'}),
            {'format': 'csv'},
        )
        content_lines = response.content.splitlines()
        reader = csv.reader(line.decode('utf-8') for line in content_lines)

        # Number of rows in reader, minus 1 for the header, should
        # equal total number of incidents.
        self.assertEqual(
            len(list(reader)) - 1,
            IncidentPage.objects.count(),
        )

    def test_csv_columns_are_in_same_order_as_json_keys(self):
        json_response = self.client.get(
            reverse('incidentpage-list', kwargs={'version': 'edge'}),
        )
        csv_response = self.client.get(
            reverse('incidentpage-list', kwargs={'version': 'edge'}),
            {'format': 'csv'},
        )

        json_keys = list(json_response.json()[0].keys())
        content_lines = csv_response.content.splitlines()
        reader = csv.reader(line.decode('utf-8') for line in content_lines)
        csv_headers = next(reader)

        self.assertEqual(json_keys, csv_headers)

    def test_csv_supports_dynamic_fields(self):
        response = self.client.get(
            reverse('incidentpage-list', kwargs={'version': 'edge'}),
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
            reverse('incidentpage-list', kwargs={'version': 'edge'}),
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
                'first_published_at': inc.first_published_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'last_published_at': inc.last_published_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'latest_revision_created_at': inc.latest_revision_created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
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
                'latitude': '',
                'longitude': '',
                'introduction': str(inc.introduction),
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
                'case_number': inc.case_number,
                'case_type': inc.case_type,
                'case_statuses': ', '.join([dict(choices.CASE_STATUS)[status] for status in inc.case_statuses]),
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
                'name_of_business': inc.name_of_business,
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
            reverse('incidentpage-list', kwargs={'version': 'edge'}),
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
            'introduction',
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
            'case_number',
            'case_type',
            'case_statuses',
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
            'name_of_business',
            'third_party_business',
            'legal_order_type',
            'status_of_prior_restraint',
            'targeted_journalists',
            'targeted_institutions',
            'tags',
            'current_charges',
            'dropped_charges',
            'politicians_or_public_figures_involved',
            'longitude',
            'latitude',
        }

        self.assertEqual(
            set(headers), expected_headers,
        )
