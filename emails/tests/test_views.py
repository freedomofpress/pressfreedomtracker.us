from django.urls import reverse
from django.test import TestCase

from emails.models import EmailSignup


class EmailSignupTest(TestCase):
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
