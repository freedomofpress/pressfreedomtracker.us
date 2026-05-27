import json
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils.http import urlencode

from wagtail.documents.models import Document
from wagtail.models import Site
from wagtail.test.utils import WagtailTestUtils

import requests
from mailchimp_marketing.api_client import ApiClientError
from taggit.models import Tag

from common.utils import ApiError
from common.views import csrf_failure
from emails.devdata import EmailSettingsFactory
from emails.models import Subscription

from .factories import SimplePageFactory


User = get_user_model()


class DocumentDownloadTest(TestCase):
    def test_serve_inline(self):
        document = Document(title="Test")
        document.file.save(
            "test_serve_inline.txt",
            ContentFile("A test content."),
        )

        response = self.client.get(
            reverse(
                "wagtaildocs_serve",
                args=(document.pk, document.filename),
            )
        )

        self.assertEqual(
            response["content-disposition"],
            'inline; filename="{}"'.format(document.filename),
        )


class AdminVersionTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_superuser(
            username="test", password="test", email="test@test.com"
        )
        self.client.force_login(user)

    def test_full_version_url_returns_200_status(self):
        self.response = self.client.get("/admin/version/")
        self.assertEqual(self.response.status_code, 200)

    @mock.patch("common.views.open")
    def test_full_version_url_returns_200_status_filenotfound(self, mock_open):
        mock_open.side_effect = FileNotFoundError
        self.response = self.client.get("/admin/version/")
        self.assertEqual(self.response.status_code, 200)


class AdminCheckNodeChartHealth(TestCase):
    def setUp(self):
        user = User.objects.create_superuser(
            username="test", password="test", email="test@test.com"
        )
        self.client.force_login(user)

    def test_check_chart_health_url_returns_200_status(self):
        response = self.client.get(reverse("check_chart_health"))
        self.assertEqual(response.status_code, 200)

    def test_check_chart_health_url_returns_ok_text(self):
        response = self.client.get(reverse("check_chart_health"))
        self.assertContains(response, "<p>ok</p>")

    @mock.patch("requests.get")
    def test_check_chart_health_timeout_informs_user(self, mock_requests):
        mock_requests.side_effect = requests.exceptions.Timeout

        response = self.client.get(reverse("check_chart_health"))
        self.assertContains(response, "Timed out")

    @mock.patch("requests.get")
    def test_check_chart_health_too_many_redirects_informs_user(self, mock_requests):
        mock_requests.side_effect = requests.exceptions.TooManyRedirects

        response = self.client.get(reverse("check_chart_health"))
        self.assertContains(response, "Too many redirects")

    @mock.patch("requests.get")
    def test_check_chart_health_other_error_informs_user(self, mock_requests):
        mock_requests.side_effect = requests.exceptions.ConnectionError

        response = self.client.get(reverse("check_chart_health"))
        self.assertContains(response, "Request exception")


class CsrfTokenViewTest(TestCase):
    def test_health_check_url_returns_200_status(self):
        self.response = self.client.get(reverse("csrf_token"))
        self.assertEqual(self.response.status_code, 200)


class MailchimpInterestViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="testadmin", is_superuser=True)

    def setUp(self):
        fake_mc_data = mock.Mock()
        fake_mc_data.get_all_lists.return_value = {
            "lists": [{"id": "1", "name": "Test List"}]
        }
        fake_mc_data.get_list_interest_categories.return_value = {
            "categories": [{"id": "2", "title": "Test Category"}]
        }
        fake_mc_data.list_interest_category_interests.return_value = {
            "interests": [{"id": "3", "name": "Test Group"}]
        }

        self.mailchimp_lists = fake_mc_data

    def test_view_forbidden_if_not_logged_in(self):
        target_url = reverse("mailchimp_interests")
        response = self.client.get(target_url)
        expected_url = (
            reverse("wagtailadmin_login") + "?" + urlencode({"next": target_url})
        )
        self.assertRedirects(response, expected_url)

    def test_view_reports_error_if_no_api_key(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("mailchimp_interests"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context_data["error"],
            "Mailchimp API key not found",
        )

    @override_settings(MAILCHIMP_API_KEY="KEY1")
    @mock.patch("mailchimp_marketing.Client")
    def test_view_reports_error_if_request_fails(self, mock_mailchimp_client):
        instance = mock_mailchimp_client.return_value
        instance.lists = mock.PropertyMock()
        instance.lists.get_all_lists.side_effect = ApiClientError(
            text="Cannot reverse the polarity"
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse("mailchimp_interests"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context_data["error"],
            "Error connecting to Mailchimp: Cannot reverse the polarity",
        )

    @override_settings(MAILCHIMP_API_KEY="KEY1")
    @mock.patch("mailchimp_marketing.Client")
    def test_view_succeeds_if_logged_in(self, mock_mailchimp_client):
        instance = mock_mailchimp_client.return_value
        instance.lists = self.mailchimp_lists

        self.client.force_login(self.user)
        response = self.client.get(reverse("mailchimp_interests"))
        self.assertEqual(response.status_code, 200)

    @override_settings(MAILCHIMP_API_KEY="KEY1")
    @mock.patch("mailchimp_marketing.Client")
    def test_view_includes_interest_and_audience_ids(self, mock_mailchimp_client):
        instance = mock_mailchimp_client.return_value
        instance.lists = self.mailchimp_lists

        self.client.force_login(self.user)
        response = self.client.get(reverse("mailchimp_interests"))
        self.assertEqual(
            response.context_data["table_data"],
            [("Test List", "1", "Test Category", "Test Group", "3")],
        )


class SubscribeForSiteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.email_settings_page = EmailSettingsFactory(site=cls.site)

    def test_ajax_subscribe_view_for_invalid_json_yields_400(self):
        self.response = self.client.post(
            reverse("subscribe_for_site"),
            headers={"accept": "application/json"},
            content_type="application/json",
            data="invalid-json",
        )
        self.assertEqual(self.response.status_code, 400)

    def test_ajax_subscribe_view_with_missing_email_yields_400(self):
        self.response = self.client.post(
            reverse("subscribe_for_site"),
            headers={"accept": "application/json"},
            content_type="application/json",
            data=json.dumps({"vegetable": "radish"}),
        )
        self.assertEqual(self.response.status_code, 400)

    @mock.patch("common.views.subscribe_for_site")
    def test_subscribe_view_ajax_succeeds(self, mock_subscribe):
        email = "test3@example.com"
        self.response = self.client.post(
            reverse("subscribe_for_site"),
            headers={"accept": "application/json"},
            content_type="application/json",
            data=json.dumps({"email": email}),
        )
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response.json(), {"success": True})
        mock_subscribe.assert_called_once_with(
            self.site, Subscription(email=email, full_name=None)
        )

    @mock.patch("common.views.subscribe_for_site")
    def test_subscribe_view_handles_subscription_errors(self, mock_subscribe):
        mock_subscribe.side_effect = ApiError(text="error", status_code=404)
        response = self.client.post(
            reverse("subscribe_for_site"),
            headers={"accept": "application/json", "cf-connecting-ip": "8.8.8.8"},
            content_type="application/json",
            data=json.dumps({"email": "test4@example.com"}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["success"])

    @mock.patch("common.views.subscribe_for_site")
    def test_subscribe_view_nonajax_handles_subscription_errors(self, mock_subscribe):
        mock_subscribe.side_effect = ApiError(text="error", status_code=404)
        response = self.client.post(
            reverse("subscribe_for_site"),
            {"email": "test4@example.com"},
            headers={"accept": "text/html"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "common/_subscribe_error.html")
        self.assertIn(
            "An internal error occurred",
            response.content.decode("utf-8"),
        )

    @mock.patch("common.views.subscribe_for_site")
    def test_subscribe_view_nonajax_succeeds(self, mock_subscribe):
        email = "test3@example.com"
        self.response = self.client.post(
            reverse("subscribe_for_site"),
            {"email": email},
            headers={"accept": "text/html"},
        )
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "common/_subscribe_thanks.html")
        mock_subscribe.assert_called_once_with(
            self.site, Subscription(email=email, full_name=None)
        )

    @mock.patch("common.views.subscribe_for_site")
    def test_subscribe_view_accept_any_succeeds(self, mock_subscribe):
        email = "test3@example.com"
        self.response = self.client.post(
            reverse("subscribe_for_site"),
            {"email": email},
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            },
        )
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "common/_subscribe_thanks.html")
        mock_subscribe.assert_called_once_with(
            self.site, Subscription(email=email, full_name=None)
        )

    def test_subscribe_view_content_type_not_form_data_fails(self):
        email = "test3@example.com"
        self.response = self.client.post(
            reverse("subscribe_for_site"),
            {"email": email},
            headers={"accept": "*/*"},
            content_type="text/html",
        )
        self.assertEqual(self.response.status_code, 400)

    def test_nonajax_subscribe_view_with_missing_email_yields_error_message(self):
        response = self.client.post(
            reverse("subscribe_for_site"),
            {"vegetable": "radish"},
            headers={"accept": "text/html"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Invalid data submitted",
            response.content.decode("utf-8"),
        )


class HealthCheckTestCase(TestCase):
    def test_health_check_url_returns_200_status(self):
        self.response = self.client.get("/health/ok/")
        self.assertEqual(self.response.status_code, 200)

    def test_version_info_url_returns_200_status(self):
        self.response = self.client.get("/health/version/")
        self.assertEqual(self.response.status_code, 200)

    @mock.patch("common.views.open")
    def test_version_info_url_returns_200_status_filenotfound(self, mock_open):
        mock_open.side_effect = FileNotFoundError
        self.response = self.client.get("/health/version/")
        self.assertEqual(self.response.status_code, 200)


class CsrfFailureTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.page = SimplePageFactory(parent=cls.site.root_page)

    def setUp(self):
        self.factory = RequestFactory()

    def test_returns_403_for_non_wagtail_page_objects(self):
        request = self.factory.post(reverse("wagtailadmin_login"))

        response = csrf_failure(request)
        self.assertEqual(response.status_code, 403)

    def test_returns_403_for_non_formpage_objects(self):
        request = self.factory.post(self.page.get_url())

        response = csrf_failure(request)
        self.assertEqual(response.status_code, 403)

    def test_returns_403_if_site_not_present(self):
        self.site.delete()
        request = self.factory.post(self.page.get_url())

        response = csrf_failure(request)
        self.assertEqual(response.status_code, 403)


class TestTagAdmin(TestCase, WagtailTestUtils):
    @classmethod
    def setUpTestData(cls):
        Tag.objects.create(name="Coffee", slug="coffee")

    def setUp(self):
        self.login()

    def get_admin_response(self):
        return self.client.get(reverse("wagtailsnippets_taggit_tag:list"))

    def test_contains_count_column(self):
        response = self.get_admin_response()
        self.assertContains(response, "Tagged item count")


class TooManyRequestsTestCase(TestCase):
    def test_too_many_requests_uses_correct_template(self):
        with self.assertTemplateUsed("429.html"):
            self.response = self.client.get(reverse("too_many_requests"))
