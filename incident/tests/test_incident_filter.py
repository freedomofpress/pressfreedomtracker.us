from django.test import TestCase

from common.tests.factories import CategoryPageFactory
from incident.utils.incident_filter import IncidentFilter


class CategoryFiltersTest(TestCase):
    def setUp(self):
        self.category = CategoryPageFactory(title='Denial of Access')

    def test_includes_category_filters(self):
        incident_filter = IncidentFilter({
            'categories': str(self.category.id),
        })
        incident_filter.clean()
        self.assertEqual(
            {f.name for f in incident_filter.filters},
            set(IncidentFilter.base_filters) | {'politicians_or_public_figures_involved'}
        )
