from datetime import date

from django.test import TestCase

from common.utils import format_date


class APStyleDatesTestCase(TestCase):
    def test_abbreviates_months_in_ap_style(self):
        self.assertEqual(format_date(date(2024, 9, 5)), "Sept. 5, 2024")
        self.assertEqual(format_date(date(2024, 5, 25)), "May 25, 2024")
