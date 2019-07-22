from django.test import TestCase
from wagtail.core.models import Site

from forms.tests.factories import FormPageFactory


class FormPageTest(TestCase):
    def test_cache_control_header_private(self):
        site = Site.objects.get()
        form_page = FormPageFactory(parent=site.root_page)

        response = self.client.get(form_page.get_url())

        self.assertEqual(response['cache-control'], 'private')
