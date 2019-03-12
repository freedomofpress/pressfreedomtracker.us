from django.test import TestCase
from django.core.management import call_command
from wagtail.core.models import Site

from common.models import (
    CategoryPage,
    CategoryIncidentFilter,
    TaxonomyCategoryPage,
)
from home.models import HomePage


class CreateCategoriesCommand(TestCase):
    def test_idempotent(self):
        """Should not create extra data."""
        CategoryPage.objects.all().delete()
        CategoryIncidentFilter.objects.all().delete()
        TaxonomyCategoryPage.objects.all().delete()
        HomePage.objects.all().delete()
        Site.objects.all().delete()

        call_command('createcategories')

        first_category_count = CategoryPage.objects.count()
        first_category_incident_filter_count = CategoryIncidentFilter.objects.count()
        first_taxonomy_category_count = TaxonomyCategoryPage.objects.count()
        first_home_count = HomePage.objects.count()
        first_site_count = Site.objects.filter(is_default_site=True).count()

        self.assertGreater(first_category_count, 0)
        self.assertGreater(first_category_incident_filter_count, 0)
        self.assertGreater(first_taxonomy_category_count, 0)
        self.assertGreater(first_home_count, 0)
        self.assertGreater(first_site_count, 0)

        call_command('createcategories')

        second_category_count = CategoryPage.objects.count()
        second_category_incident_filter_count = CategoryIncidentFilter.objects.count()
        second_taxonomy_category_count = TaxonomyCategoryPage.objects.count()
        second_home_count = HomePage.objects.count()
        second_site_count = Site.objects.filter(is_default_site=True).count()

        self.assertEqual(first_category_count, second_category_count)
        self.assertEqual(first_category_incident_filter_count, second_category_incident_filter_count)
        self.assertEqual(first_taxonomy_category_count, second_taxonomy_category_count)
        self.assertEqual(first_home_count, second_home_count)
        self.assertEqual(first_site_count, second_site_count)
