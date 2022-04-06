from django.test import TestCase

from forms.wagtail_hooks import global_admin_css


class TestFormsHooks(TestCase):
    def test_css_in_admin(self):
        self.assertIn(".nested-inline .fields label", global_admin_css())
