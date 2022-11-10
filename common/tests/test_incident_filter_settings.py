from django.core.exceptions import ValidationError
from django.test import TestCase
from wagtail.models import Site

from common.models.pages import CategoryIncidentFilter
from common.models.settings import IncidentFilterSettings, GeneralIncidentFilter
from common.tests.factories import CategoryPageFactory


class IncidentFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        CategoryIncidentFilter.objects.all().delete()

    def setUp(self):
        self.category = CategoryPageFactory()
        self.site = Site.objects.get(is_default_site=True)
        self.settings = IncidentFilterSettings.for_site(self.site)

    def test_valid_incident_filter(self):
        """
        General incident filters should be fine to create if they don't conflict
        with category incident filters.
        """
        CategoryIncidentFilter.objects.create(
            category=self.category,
            incident_filter='state',
        )
        incident_filter = GeneralIncidentFilter(
            incident_filter_settings=self.settings,
            incident_filter='arrest_status',
        )
        incident_filter.clean()

    def test_incident_filter_unique_with_category(self):
        """
        Incident filters should not be useable in general settings if they're already
        being used in a category. Attempting to do so should raise a validation error.
        """
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
