from django.test import TestCase, RequestFactory
from wagtail.wagtailcore.middleware import SiteMiddleware

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
