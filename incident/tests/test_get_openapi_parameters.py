import itertools
from unittest import mock

from django.db.utils import ProgrammingError
from django.test import TestCase
from drf_spectacular.utils import OpenApiParameter
from wagtail.core.models import Site

from common.models.pages import CategoryPage
from common.models.settings import IncidentFilterSettings, GeneralIncidentFilter
from common.tests.factories import CategoryPageFactory
from incident.models import IncidentPage
from incident.utils.incident_filter import (
    get_openapi_parameters,
    IncidentFilter,
    SearchFilter,
)


class GetOpenApiParametersTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        CategoryPage.objects.all().delete()

    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.settings = IncidentFilterSettings.for_site(self.site)
        self.addTypeEqualityFunc(OpenApiParameter, self._assert_param_equal)

    def _assert_param_equal(self, lhs, rhs, msg):
        self.assertDictEqual(lhs.__dict__, rhs.__dict__, msg)

    def test_get_openapi_params_includes_search(self):
        params = get_openapi_parameters()

        self.assertEqual(len(params), 1)
        for actual, expected in zip(params, SearchFilter().openapi_parameters()):
            self.assertEqual(actual, expected)

    def test_get_openapi_params_general_and_category_fields(self):
        CategoryPageFactory(incident_filters=['arrest_status'])
        GeneralIncidentFilter.objects.create(
            incident_filter_settings=self.settings,
            incident_filter='city',
        )

        params = get_openapi_parameters()

        expected_params = itertools.chain(
            SearchFilter().openapi_parameters(),
            IncidentFilter._get_filter(
                IncidentPage._meta.get_field('city')
            ).openapi_parameters(),
            IncidentFilter._get_filter(
                IncidentPage._meta.get_field('arrest_status')
            ).openapi_parameters()
        )

        for actual, expected in zip(params, expected_params):
            self.assertEqual(actual, expected)

    @mock.patch('common.models.CategoryPage')
    def test_returns_empty_list_if_db_error(self, MockCategoryPage):
        MockCategoryPage.objects.live.side_effect = ProgrammingError
        self.assertEqual(get_openapi_parameters(), [])
