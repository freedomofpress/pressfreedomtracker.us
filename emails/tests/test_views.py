from django.core.cache import cache
from django.urls import reverse
from django.test import TestCase

from emails.models import EmailSignup


class EmailSignupTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_successful_signup(self):
        response = self.client.post(
            reverse("email-signup-create"), {"email_address": "hello@example.com"}
        )
        self.assertEqual(response.status_code, 200)

        # should not raise error
        EmailSignup.objects.get(email_address="hello@example.com")

    def test_should_reject_posts_without_email(self):
        response = self.client.post(reverse("email-signup-create"), {})
        self.assertEqual(response.status_code, 400)

    def test_should_reject_non_email_addresses(self):
        response = self.client.post(
            reverse("email-signup-create"), {"email_address": "example.com"}
        )
        self.assertEqual(response.status_code, 400)

    def test_should_reject_already_taken_emails(self):
        EmailSignup.objects.create(email_address="hello@example.com")
        response = self.client.post(
            reverse("email-signup-create"), {"email_address": "hello@example.com"}
        )
        self.assertEqual(response.status_code, 400)

    def test_signup_should_permit_leading_or_trailing_whitespace(self):
        response = self.client.post(
            reverse("email-signup-create"), {"email_address": "  hello@example.com    "}
        )
        self.assertEqual(response.status_code, 200)

        # should not raise error
        EmailSignup.objects.get(email_address="hello@example.com")


class EmailSignupThrottleTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_throttling(self):
        for i in range(20):
            with self.subTest(i=i):
                response = self.client.post(
                    reverse("email-signup-create"),
                    {"email_address": f'hello{i}@example.com'},
                )
                self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse("email-signup-create"),
            {"email_address": "name@example.com"},
        )
        self.assertEqual(response.status_code, 429)

    def test_throttling_using_cloudflare_headers(self):
        ip1 = '1.1.1.1'
        ip2 = '2.2.2.2'

        for i in range(40):
            with self.subTest(i=i):
                ip = ip1 if i % 2 == 0 else ip2
                response = self.client.post(
                    reverse("email-signup-create"),
                    {"email_address": f'hello{i}@example.com'},
                    HTTP_CF_CONNECTING_IP=ip,
                )
                self.assertEqual(response.status_code, 200)
        response = self.client.post(
            reverse("email-signup-create"),
            {"email_address": "name@example.com"},
            HTTP_CF_CONNECTING_IP=ip1,
        )
        self.assertEqual(response.status_code, 429)
        response = self.client.post(
            reverse("email-signup-create"),
            {"email_address": "name@example.com"},
            HTTP_CF_CONNECTING_IP=ip2,
        )
        self.assertEqual(response.status_code, 429)
