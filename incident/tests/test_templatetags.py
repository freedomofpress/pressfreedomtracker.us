from django.test import SimpleTestCase

from incident.templatetags import case_tags, subpoena_tags


class TestTemplatetags(SimpleTestCase):
    def test_case_status_display(self):
        self.assertEqual(case_tags.get_case_status_display("ONGOING"), "ongoing")

    def test_subpoena_status_display(self):
        self.assertEqual(
            subpoena_tags.get_subpoena_status_display("PENDING"), "pending"
        )
