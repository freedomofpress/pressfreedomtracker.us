from django.test import TestCase, RequestFactory, Client
from wagtail.models import Site

from .factories import FormPageFactory


class CsrfFailureTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.form_page = FormPageFactory(parent=site.root_page)

    def setUp(self):
        self.csrf_client = Client(enforce_csrf_checks=True)
        self.factory = RequestFactory()

    def test_csrf_failure_redirects_to_original_form_page(self):
        submission_data = {}
        for field in self.form_page.get_form_fields():
            submission_data[field.clean_name] = 'value'
        response = self.csrf_client.post(
            self.form_page.get_url(),
            data=submission_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            self.form_page.get_url(),
        )
        self.assertEqual(
            response.context['top_level_error'],
            'Submission failed, please try again.',
        )
        form = response.context['form']
        self.assertEqual(form.initial, submission_data)
