from django.test import TestCase
from wagtail.core.models import Site

import incident.tests.factories as incident_factories
from common.models.pages import CategoryPage
from common.models.settings import IncidentFilterSettings, GeneralIncidentFilter
from common.tests.factories import CategoryPageFactory
from incident.models.choices import ARREST_STATUS
from incident.utils.incident_filter import get_serialized_filters


class GetSerializedFiltersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        CategoryPage.objects.all().delete()

    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.settings = IncidentFilterSettings.for_site(self.site)

    def test_serialize_general__search_only(self):
        serialized = get_serialized_filters()
        self.assertEqual(serialized, [
            {
                'id': -1,
                'title': 'General',
                'filters': [
                    {
                        'title': 'Search terms',
                        'type': 'text',
                        'name': 'search',
                    }
                ]
            },
        ])

    def test_serialized_filters_includes_autocomplete_choices(self):
        self.maxDiff = 9999
        category = CategoryPageFactory(incident_filters=[
            'arresting_authority',
            'target_nationality',
            'targeted_journalists',
            'charges',
            'equipment_seized',
        ])

        leos = incident_factories.LawEnforcementOrganizationFactory.create_batch(3)
        nats = incident_factories.NationalityFactory.create_batch(3)
        journalists = incident_factories.JournalistFactory.create_batch(3)
        charges = incident_factories.ChargeFactory.create_batch(3)
        incident = incident_factories.IncidentPageFactory()
        equipment_seized = incident_factories.EquipmentSeizedFactory.create_batch(3, incident=incident)

        serialized = get_serialized_filters()

        self.assertEqual(serialized, [
            {
                'id': -1,
                'title': 'General',
                'filters': [
                    {
                        'title': 'Search terms',
                        'type': 'text',
                        'name': 'search',
                    },
                ]
            },
            {
                'id': category.pk,
                'title': category.title,
                'url': category.url,
                'symbol': category.page_symbol,
                'filters': [
                    {
                        'title': 'Arresting authority',
                        'many': False,
                        'type': 'autocomplete',
                        'autocomplete_type': 'incident.LawEnforcementOrganization',
                        'name': 'arresting_authority',
                        'choices': [leo.title for leo in leos],
                    },
                    {
                        'title': 'Target Nationality',
                        'many': True,
                        'type': 'autocomplete',
                        'autocomplete_type': 'incident.Nationality',
                        'name': 'target_nationality',
                        'choices': [nat.title for nat in nats],
                    },
                    {
                        'title': 'Targeted any of these journalists',
                        'many': True,
                        'type': 'autocomplete',
                        'autocomplete_type': 'incident.Journalist',
                        'name': 'targeted_journalists',
                        'choices': [j.title for j in journalists],
                    },
                    {
                        'title': 'Charges',
                        'type': 'autocomplete',
                        'name': 'charges',
                        'autocomplete_type': 'incident.Charge',
                        'choices': [c.title for c in charges],
                    },
                    {
                        'title': 'Equipment Seized',
                        'type': 'autocomplete',
                        'name': 'equipment_seized',
                        'autocomplete_type': 'incident.Equipment',
                        'many': True,
                        'choices': [es.equipment.name for es in equipment_seized],
                    }
                ]
            }
        ])

    def test_serialize_general_and_category_fields(self):
        category = CategoryPageFactory(incident_filters=['arrest_status'])
        GeneralIncidentFilter.objects.create(
            incident_filter_settings=self.settings,
            incident_filter='city',
        )

        serialized = get_serialized_filters()
        self.assertEqual(serialized, [
            {
                'id': -1,
                'title': 'General',
                'filters': [
                    {
                        'title': 'Search terms',
                        'type': 'text',
                        'name': 'search',
                    },
                    {
                        'title': 'City',
                        'type': 'text',
                        'name': 'city',
                    },
                ]
            },
            {
                'id': category.id,
                'title': category.title,
                'url': category.url,
                'symbol': category.page_symbol,
                'filters': [
                    {
                        'title': 'Arrest status',
                        'type': 'choice',
                        'name': 'arrest_status',
                        'choices': ARREST_STATUS,
                    }
                ]
            },

        ])
