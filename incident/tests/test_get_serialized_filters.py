from django.test import TestCase
from wagtail.wagtailcore.models import Site

from common.models.pages import CategoryIncidentFilter
from common.models.settings import IncidentFilterSettings, GeneralIncidentFilter
from common.tests.factories import CategoryPageFactory
from incident.models.choices import ARREST_STATUS
from incident.utils.incident_filter import get_serialized_filters


class GetSerializedFiltersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        CategoryIncidentFilter.objects.all().delete()

    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.settings = IncidentFilterSettings.for_site(self.site)

    def test_serialize_general__search_only(self):
        serialized = get_serialized_filters()
        self.assertEqual(serialized, [
            {
                'id': -1,
                'title': 'General',
                'enabled': True,
                'filters': [
                    {
                        'title': 'Search',
                        'type': 'text',
                        'name': 'search',
                    }
                ]
            },
        ])

    def test_serialize_general_and_category_fields(self):
        category = CategoryPageFactory(incident_filters=['arrest_status'])
        GeneralIncidentFilter.objects.create(
            incident_filter_settings=self.settings,
            incident_filter='affiliation',
        )

        serialized = get_serialized_filters()
        self.assertEqual(serialized, [
            {
                'id': -1,
                'title': 'General',
                'enabled': True,
                'filters': [
                    {
                        'title': 'Search',
                        'type': 'text',
                        'name': 'search',
                    },
                    {
                        'title': 'Affiliation',
                        'type': 'text',
                        'name': 'affiliation',
                    },
                ]
            },
            {
                'id': category.id,
                'title': category.title,
                'url': category.url,
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
