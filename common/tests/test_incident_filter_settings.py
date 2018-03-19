from django.core.exceptions import ValidationError
from django.test import TestCase
from wagtail.wagtailcore.models import Site

from common.models.pages import CategoryIncidentFilter
from common.models.settings import IncidentFilterSettings, GeneralIncidentFilter
from common.tests.factories import CategoryPageFactory


class IncidentFilterTest(TestCase):
    def setUp(self):
        self.category = CategoryPageFactory()
        self.site = Site.objects.get(is_default_site=True)
        self.settings = IncidentFilterSettings.for_site(self.site)

    def test_valid_incident_filter(self):
        incident_filter = GeneralIncidentFilter(
            incident_filter_settings=self.settings,
            incident_filter='arrest_status',
        )
        incident_filter.clean()

    def test_incident_filter_unique_with_category(self):
        CategoryIncidentFilter.objects.create(
            category=self.category,
            incident_filter='arrest_status',
        )

        incident_filter = GeneralIncidentFilter(
            incident_filter_settings=self.settings,
            incident_filter='arrest_status',
        )

        with self.assertRaises(ValidationError):
            incident_filter.clean()
