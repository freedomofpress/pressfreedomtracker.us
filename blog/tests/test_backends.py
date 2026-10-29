from django.test import SimpleTestCase

from wagtail_newsletter.campaign_backends import get_backend

from blog.backends import DisableTrackingBackend


class DisableTrackingBackendTestCase(SimpleTestCase):
    def test_configured_backend_disables_all_tracking(self):
        backend = get_backend()
        self.assertIsInstance(backend, DisableTrackingBackend)

        body = backend.get_campaign_request_body(
            recipients=None,
            from_name="U.S. Press Freedom Tracker",
            reply_to="newsletter@pressfreedomtracker.us",
            subject="Test",
        )

        self.assertEqual(
            body["tracking"],
            {"opens": False, "html_clicks": False, "text_clicks": False},
        )
        self.assertEqual(body["settings"]["subject_line"], "Test")
