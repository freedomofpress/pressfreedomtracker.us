from django.core.exceptions import ValidationError
from django.test import TestCase, RequestFactory
from wagtail.wagtailcore.middleware import SiteMiddleware
from wagtail.wagtailcore.models import Site

from common.models.pages import CategoryIncidentFilter
from common.models.settings import IncidentFilterSettings, GeneralIncidentFilter
from common.tests.factories import CategoryPageFactory
from incident.tests.factories import IncidentPageFactory


class ContextTest(TestCase):
    def test_incidents_filtered_by_category(self):
        category1 = CategoryPageFactory()
        category2 = CategoryPageFactory()
        incident1 = IncidentPageFactory(categories=[category1])
        IncidentPageFactory(title='Not relevant', categories=[category2])

        request = RequestFactory().get('/')
        # Attach wagtail site.
        SiteMiddleware().process_request(request)

        context = category1.get_context(request)

        self.assertEqual(set(context['entries_page']), {incident1})

    def test_incidents_filtered_by_category__and_choice(self):
        category1 = CategoryPageFactory(incident_filters=['arrest_status'])
        category2 = CategoryPageFactory()
        incident1 = IncidentPageFactory(categories=[category1], arrest_status='DETAINED_NO_PROCESSING')
        IncidentPageFactory(title='Not choice', categories=[category1], arrest_status='UNKNOWN')
        IncidentPageFactory(title='Not category', categories=[category2])

        request = RequestFactory().get('/', {'arrest_status': 'DETAINED_NO_PROCESSING'})
        # Attach wagtail site.
        SiteMiddleware().process_request(request)

        context = category1.get_context(request)

        self.assertEqual(set(context['entries_page']), {incident1})

    def test_filtered__has_filter(self):
        """
        CategoryPage context method should correctly detect if any filters
        are present
        """
        category_page = CategoryPageFactory()
        request = RequestFactory().get(
            '/',
            {'arrest_status': 'DETAINED_NO_PROCESSING'}
        )
        # Attach wagtail site.
        SiteMiddleware().process_request(request)
        context = category_page.get_context(request)
        self.assertTrue(context['filtered'])

    def test_filtered__no_filter(self):
        """
        CategoryPage context method should correctly detect if no filters
        are present
        """
        category_page = CategoryPageFactory()
        request = RequestFactory().get('/')
        # Attach wagtail site.
        SiteMiddleware().process_request(request)
        context = category_page.get_context(request)
        self.assertFalse(context['filtered'])

    def test_filtered__ignore_page(self):
        """
        CategoryPage context method should not count `page` in `request.GET` as
        a filter, since it is just a pagination implementation detail
        """
        category_page = CategoryPageFactory()
        request = RequestFactory().get('/', {'page': '2'})
        # Attach wagtail site.
        SiteMiddleware().process_request(request)
        context = category_page.get_context(request)
        self.assertFalse(context['filtered'])

    def test_filtered__ignore_categories(self):
        """
        CategoryPage context method should not count `category` in
        `request.GET` as a filter since the page is limited by category
        already and the `category` querystring entry is redundant
        """
        category_page = CategoryPageFactory()
        request = RequestFactory().get('/', {'categories': '1'})
        # Attach wagtail site.
        SiteMiddleware().process_request(request)
        context = category_page.get_context(request)
        self.assertFalse(context['filtered'])


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
        Category incident filters should be fine to create if they don't conflict
        with general incident filters.
        """
        GeneralIncidentFilter.objects.create(
            incident_filter_settings=self.settings,
            incident_filter='state',
        )
        incident_filter = CategoryIncidentFilter(
            category=self.category,
            incident_filter='arrest_status',
        )
        incident_filter.clean()

    def test_incident_filter_unique_with_settings(self):
        """
        Incident filters should not be useable in categories if they're already
        being used in general incident filter settings. Attempting to do so should
        raise a validation error.
        """
        GeneralIncidentFilter.objects.create(
            incident_filter_settings=self.settings,
            incident_filter='arrest_status',
        )

        incident_filter = CategoryIncidentFilter(
            category=self.category,
            incident_filter='arrest_status',
        )

        with self.assertRaises(ValidationError):
            incident_filter.clean()
