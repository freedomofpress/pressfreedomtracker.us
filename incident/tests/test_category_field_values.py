import datetime
import re
import urllib.parse
from functools import partial

from bs4 import BeautifulSoup
from django.test import TestCase
from django.utils.text import capfirst
from django.utils.html import strip_tags

from common.tests.factories import CategoryPageFactory
from incident.models import CAT_FIELD_VALUES, IncidentPage
from incident.models import choices
from incident.tests.factories import (
    IncidentPageFactory,
    IncidentIndexPageFactory,
    IncidentChargeFactory,
    IncidentChargeWithUpdatesFactory,
    EquipmentBrokenFactory,
    EquipmentSeizedFactory,
    LawEnforcementOrganizationFactory,
    NationalityFactory,
    GovernmentWorkerFactory,
    PoliticianOrPublicFactory,
    LegalOrderFactory,
)


def querystring_matches(expected_qs, url):
    """Returns True if the querystring in the url matches the expected
    value, False otherwise.

    `expected_qs` is a dictionary of querystring keys and values,
    formatted as in the output of parse_qs, see
    https://docs.python.org/3/library/urllib.parse.html#urllib.parse.parse_qs

    `url` is a URL string.

    """
    parsed = urllib.parse.urlparse(url)
    return expected_qs == urllib.parse.parse_qs(parsed.query)


class TestCategoryFieldValuesByField(TestCase):
    def setUp(self):
        self.index = IncidentIndexPageFactory()
        self.category = CategoryPageFactory()
        self.quoted_category_title = urllib.parse.quote(self.category.title)
        self.incident = IncidentPageFactory(
            parent=self.index,
            unnecessary_use_of_force=True,

        )

    def assert_link_exists(self, html, text, querystring_params):
        """Given an HTML string, assert that a link exists matching
        the given text and querystring parameters.

        `querystring_params` should be a dictionary of querystring
        key/value pairs.

        """
        escaped_text = re.escape(text)
        parsed = BeautifulSoup(html, 'html.parser')
        self.assertIsNotNone(
            parsed.find(
                'a',
                href=partial(querystring_matches, {
                    k: [v] for k, v in querystring_params.items()
                }),
                string=re.compile(fr'\s*{escaped_text}\s*'),
            ),
            f'Link with text {text!r} and querystring parameters {querystring_params} not found in {html}'
        )

    def assert_text(self, field_name, render_function):
        setattr(self.incident, field_name, 'Text')
        output = render_function(self.incident, field_name, self.index, self.category)
        self.assert_link_exists(
            output,
            'Text',
            {field_name: 'Text', 'categories': self.category.title},
        )

    def assert_choices(self, field_name, render_function):
        field = IncidentPage._meta.get_field(field_name)
        for choice_value, choice_name in field.choices:
            setattr(self.incident, field_name, choice_value)
            output = render_function(self.incident, field_name, self.index, self.category)

            pretty_name = capfirst(
                getattr(self.incident, f'get_{field_name}_display')()
            )
            self.assert_link_exists(output, pretty_name, {
                field_name: choice_value,
                'categories': self.category.title,
            })
        setattr(self.incident, field_name, '')
        output = render_function(self.incident, field_name, self.index, self.category)
        self.assertEqual(output, '')

    def assert_many_relationship(self, field_name, render_function):
        output = render_function(self.incident, field_name, self.index, self.category)
        for item in getattr(self.incident, field_name).all():
            self.assert_link_exists(
                output,
                item.title,
                {field_name: item.title},
            )
        getattr(self.incident, field_name).clear()
        output = render_function(self.incident, field_name, self.index, self.category)
        self.assertEqual(output, '')

    def assert_charges(self, field_name, render_function):
        output = render_function(self.incident, field_name, self.index, self.category)
        for incident_charge in getattr(self.incident, field_name).all():
            self.assert_link_exists(
                output,
                incident_charge.charge.title,
                {field_name: incident_charge.charge.title},
            )
            for date, status in incident_charge.entries_display():
                self.assertIn(date, output)
                self.assertIn(status.capitalize(), output)
        getattr(self.incident, field_name).clear()
        output = render_function(self.incident, field_name, self.index, self.category)
        self.assertEqual(output, '')

    def assert_legal_orders(self, field_name, render_function):
        output = render_function(self.incident, field_name, self.index, self.category)
        for legal_order in getattr(self.incident, field_name).all():
            self.assert_link_exists(
                output,
                legal_order.get_order_type_display(),
                {'legal_order_type': legal_order.order_type}
            )
            self.assert_link_exists(
                output,
                legal_order.get_information_requested_display(),
                {'legal_order_information_requested': legal_order.information_requested},
            )
            for date, status in legal_order.entries_display():
                self.assertIn(date, output)
                self.assertIn(status.capitalize(), output)
        getattr(self.incident, field_name).clear()
        output = render_function(self.incident, field_name, self.index, self.category)
        self.assertEqual(output, '')

    def assert_equipment(self, field_name, render_function):
        output = render_function(self.incident, field_name, self.index, self.category)
        for item in getattr(self.incident, field_name).all():
            self.assert_link_exists(
                output,
                item.equipment.name,
                {field_name: item.equipment.name},
            )
        getattr(self.incident, field_name).clear()
        output = render_function(self.incident, field_name, self.index, self.category)
        self.assertEqual(output, '')

    def assert_date(self, field_name, render_function):
        output = render_function(self.incident, field_name, self.index, self.category)
        value = getattr(self.incident, field_name)
        self.assertIn(f'{field_name}_upper={value:%Y-%m-%d}', output)
        self.assertIn(f'{field_name}_lower={value:%Y-%m-%d}', output)
        self.assertIn(f'{value:%B %-d, %Y}', output)
        setattr(self.incident, field_name, None)
        self.assertEqual(render_function(self.incident, field_name, self.index, self.category), '')

    def assert_boolean(self, field_name, render_function):
        setattr(self.incident, field_name, True)
        output = render_function(self.incident, field_name, self.index, self.category)
        self.assert_link_exists(
            output,
            'Yes',
            {field_name: '1'},
        )
        setattr(self.incident, field_name, False)
        output = render_function(self.incident, field_name, self.index, self.category)
        self.assert_link_exists(
            output,
            'No',
            {field_name: '0'},
        )

    def test_arrest_status(self):
        self.assert_choices(
            'arrest_status',
            CAT_FIELD_VALUES['arrest_status'],
        )

    def test_status_of_charges(self):
        self.assert_choices(
            'status_of_charges',
            CAT_FIELD_VALUES['status_of_charges'],
        )

    def test_arresting_authority(self):
        output = CAT_FIELD_VALUES['arresting_authority'](self.incident, 'arresting_authority', self.index, self.category)
        self.assertEqual(output, '')

        leo = LawEnforcementOrganizationFactory(title='Los Angeles Police Department')
        self.incident.arresting_authority = leo

        output = CAT_FIELD_VALUES['arresting_authority'](self.incident, 'arresting_authority', self.index, self.category)
        self.assertIn(leo.title, strip_tags(output))
        self.assertIn(f'arresting_authority={leo.title}', output)

    def test_charges(self):
        IncidentChargeFactory(
            incident_page=self.incident,
            status='CHARGES_PENDING',
            date='2022-01-01',
        )
        self.assert_charges(
            'charges',
            CAT_FIELD_VALUES['charges'],
        )

    def test_charges_with_updates(self):
        IncidentChargeWithUpdatesFactory(
            incident_page=self.incident,
            status='UNKNOWN',
            date='2022-01-01',
            update1__status='CHARGES_PENDING',
            update1__date='2022-01-02',
            update2__status='CONVICTED',
            update2__date='2022-01-03',
            update3__status='ACQUITTED',
            update3__date='2022-01-04',
        )
        self.assert_charges(
            'charges',
            CAT_FIELD_VALUES['charges'],
        )

    def test_legal_orders(self):
        LegalOrderFactory(
            incident_page=self.incident,
            order_type=choices.LegalOrderType.NATIONAL_SECURITY_LETTER,
            information_requested=choices.InformationRequested.TESTIMONY_ABOUT_SOURCE,
            status=choices.LegalOrderStatus.PENDING,
            date='2022-01-01',
        )

        self.assert_legal_orders(
            'legal_orders',
            CAT_FIELD_VALUES['legal_orders'],
        )

    def test_politicians_or_public_figures_involved(self):
        self.incident.politicians_or_public_figures_involved = PoliticianOrPublicFactory.create_batch(2)
        self.incident.save()
        self.assert_many_relationship(
            'politicians_or_public_figures_involved',
            CAT_FIELD_VALUES['politicians_or_public_figures_involved'],
        )

    def test_workers_whose_communications_where_obtained(self):
        self.incident.workers_whose_communications_were_obtained = GovernmentWorkerFactory.create_batch(2)
        self.incident.save()
        self.assert_many_relationship(
            'workers_whose_communications_were_obtained',
            CAT_FIELD_VALUES['workers_whose_communications_were_obtained'],
        )

    def test_detention_date(self):
        self.incident.detention_date = datetime.date.today()
        self.assert_date('detention_date', CAT_FIELD_VALUES['detention_date'])

    def test_release_date(self):
        self.incident.release_date = datetime.date.today()
        self.assert_date('release_date', CAT_FIELD_VALUES['release_date'])

    def test_unnecessary_use_of_force(self):
        self.assert_boolean('unnecessary_use_of_force', CAT_FIELD_VALUES['unnecessary_use_of_force'])

    def test_charged_under_espionage_act(self):
        self.assert_boolean('charged_under_espionage_act', CAT_FIELD_VALUES['charged_under_espionage_act'])

    def test_equipment_broken(self):
        EquipmentBrokenFactory.create_batch(2, incident=self.incident)
        self.assert_equipment(
            'equipment_broken',
            CAT_FIELD_VALUES['equipment_broken'],
        )

    def test_equipment_seized(self):
        EquipmentSeizedFactory.create_batch(2, incident=self.incident)
        self.assert_equipment(
            'equipment_seized',
            CAT_FIELD_VALUES['equipment_seized'],
        )

    def test_status_of_seized_equipment(self):
        self.assert_choices(
            'status_of_seized_equipment',
            CAT_FIELD_VALUES['status_of_seized_equipment'],
        )

    def test_is_search_warrant_obtained(self):
        self.assert_boolean('is_search_warrant_obtained', CAT_FIELD_VALUES['is_search_warrant_obtained'])

    def test_actor(self):
        self.assert_choices(
            'actor',
            CAT_FIELD_VALUES['actor'],
        )

    def test_third_party_business(self):
        self.assert_choices(
            'third_party_business',
            CAT_FIELD_VALUES['third_party_business'],
        )

    def test_legal_order_type(self):
        self.assert_choices(
            'legal_order_type',
            CAT_FIELD_VALUES['legal_order_type'],
        )

    def test_legal_order_venue(self):
        self.assert_choices(
            'legal_order_venue',
            CAT_FIELD_VALUES['legal_order_venue'],
        )

    def test_status_of_prior_restraint(self):
        self.assert_choices(
            'status_of_prior_restraint',
            CAT_FIELD_VALUES['status_of_prior_restraint'],
        )

    def test_subpoena_type(self):
        self.assert_choices(
            'subpoena_type',
            CAT_FIELD_VALUES['subpoena_type'],
        )

    def test_legal_order_target(self):
        self.assert_choices(
            'legal_order_target',
            CAT_FIELD_VALUES['legal_order_target'],
        )
        self.incident.legal_order_target = choices.LegalOrderTarget.THIRD_PARTY
        self.incident.name_of_business = (
            'Business Name',
        )
        self.incident.save()
        render_function = CAT_FIELD_VALUES['legal_order_target']

        for choice_value in choices.ThirdPartyBusiness.values:
            self.incident.third_party_business = choice_value
            self.incident.save()
            output = render_function(self.incident, 'legal_order_target', self.index, self.category)
            self.assert_link_exists(
                output,
                self.incident.get_third_party_business_display(),
                {
                    'third_party_business': choice_value,
                    'categories': self.category.title,
                },
            )
            self.assert_link_exists(
                output,
                self.incident.name_of_business,
                {
                    'name_of_business': self.incident.name_of_business,
                    'categories': self.category.title,
                },
            )

            self.assert_link_exists(
                output,
                self.incident.get_legal_order_target_display(),
                {
                    'legal_order_target': self.incident.legal_order_target,
                    'categories': self.category.title,
                },
            )

    def test_subpoena_statuses(self):
        # field = IncidentPage._meta.get_field(field_name)
        self.incident.subpoena_statuses = []
        field_name = 'subpoena_statuses'
        render_function = CAT_FIELD_VALUES[field_name]
        output = render_function(self.incident, field_name, self.index, self.category)
        self.assertEqual(output, '')
        for choice_value, choice_name in choices.SUBPOENA_STATUS:
            self.incident.subpoena_statuses.append(choice_value)
            output = render_function(self.incident, field_name, self.index, self.category)
            self.assertIn(choice_name.capitalize(), output)
            self.assertIn(f'{field_name}={choice_value}', output)

    def test_target_us_citizenship_status(self):
        self.assert_choices(
            'target_us_citizenship_status',
            CAT_FIELD_VALUES['target_us_citizenship_status'],
        )

    def test_denial_of_entry(self):
        self.assert_boolean('denial_of_entry', CAT_FIELD_VALUES['denial_of_entry'])

    def test_stopped_previously(self):
        self.assert_boolean('stopped_previously', CAT_FIELD_VALUES['stopped_previously'])

    def test_did_authorities_ask_for_device_access(self):
        self.assert_choices(
            'did_authorities_ask_for_device_access',
            CAT_FIELD_VALUES['did_authorities_ask_for_device_access'],
        )

    def test_did_authorities_ask_for_social_media_user(self):
        self.assert_choices(
            'did_authorities_ask_for_social_media_user',
            CAT_FIELD_VALUES['did_authorities_ask_for_social_media_user'],
        )

    def test_did_authorities_ask_for_social_media_pass(self):
        self.assert_choices(
            'did_authorities_ask_for_social_media_pass',
            CAT_FIELD_VALUES['did_authorities_ask_for_social_media_pass'],
        )

    def test_did_authorities_ask_about_work(self):
        self.assert_choices(
            'did_authorities_ask_about_work',
            CAT_FIELD_VALUES['did_authorities_ask_about_work'],
        )

    def test_assailant(self):
        self.assert_choices(
            'assailant', CAT_FIELD_VALUES['assailant'],
        )

    def test_was_journalist_targeted(self):
        self.assert_choices(
            'was_journalist_targeted', CAT_FIELD_VALUES['was_journalist_targeted'],
        )

    def test_border_point(self):
        self.assert_text(
            'border_point',
            CAT_FIELD_VALUES['border_point'],
        )

    def test_name_of_business(self):
        self.assert_text(
            'name_of_business',
            CAT_FIELD_VALUES['name_of_business'],
        )

    def test_target_nationality(self):
        self.incident.target_nationality = NationalityFactory.create_batch(2)
        self.incident.save()
        self.assert_many_relationship(
            'target_nationality',
            CAT_FIELD_VALUES['target_nationality'],
        )


class CategoryFieldValuesCompleteness(TestCase):
    def test_all_categories_provide_details(self):
        index = IncidentIndexPageFactory()
        for category_name in IncidentPageFactory._meta.parameters.keys():
            with self.subTest(category_name=category_name):
                category = CategoryPageFactory(**{category_name: True})
                incident = IncidentPageFactory(
                    parent=index,
                    categories=[category])

                # Should succeed without errors
                incident.get_category_details()


class CategoryFieldValues(TestCase):
    """Category values"""
    def setUp(self):
        self.index = IncidentIndexPageFactory()
        self.category1 = CategoryPageFactory(
            **{'arrest': True}
        )
        self.category2 = CategoryPageFactory(
            **{'equipment_damage': True}
        )
        # Category 3 has no metadata fields
        self.category3 = CategoryPageFactory(
            **{'other_incident': True}
        )
        self.category4 = CategoryPageFactory(
            denial_of_access=True,
        )

        self.incident = IncidentPageFactory(
            parent=self.index,
            categories=[self.category3, self.category1, self.category2, self.category4],
            arrest=True,
            equipment_damage=True,
            politicians_or_public_figures_involved=3,
        )

        self.category_details = self.incident.get_category_details()

    def test_should_get_category_details(self):
        self.assertEqual(len(self.category_details.items()), 4)

    def test_should_sort_categories_without_metadata_last(self):
        self.assertEqual(
            list(self.category_details.items())[-1],
            (self.category3, []),
        )

    def test_should_get_basic_category_fields(self):
        arrest_details = self.category_details[self.category1]
        self.assertEqual(arrest_details[0]['name'], 'Arrest Status')
        self.assertIn(self.incident.arrest_status, arrest_details[0]['html'])

    def test_should_get_list_category_fields(self):
        denial_of_access_details = self.category_details[self.category4]
        self.assertEqual(
            denial_of_access_details[0]['name'],
            'Government agency or public official involved',
        )
        for item in self.incident.politicians_or_public_figures_involved.all():
            self.assertIn(item.title, denial_of_access_details[0]['html'])

    def test_should_get_charges_category_fields(self):
        arrest_details = self.category_details[self.category1]
        self.assertEqual(arrest_details[2]['name'], 'Charges')
        for charge in self.incident.charges.all():
            self.assertIn(charge.title, arrest_details[2]['html'])

    def test_should_get_equipment_list_category_fields(self):
        equipment_damage_details = self.category_details[self.category2]
        self.assertEqual(equipment_damage_details[0]['name'], 'Equipment Broken')
        for equipment_broken in self.incident.equipment_broken.all():
            self.assertIn(equipment_broken.equipment.name, equipment_damage_details[0]['html'])

    def test_should_get_date_category_fields(self):
        arrest_details = self.category_details[self.category1]

        self.assertEqual(arrest_details[3]['name'], 'Detention Date')
        self.assertIn(self.incident.detention_date.isoformat(), arrest_details[3]['html'])

    def test_should_get_boolean_category_fields(self):
        arrest_details = self.category_details[self.category1]
        self.assertEqual(arrest_details[5]['name'], 'Unnecessary use of force?')
        expected_value = '1' if self.incident.unnecessary_use_of_force else '0'
        self.assertIn(expected_value, arrest_details[5]['html'])
