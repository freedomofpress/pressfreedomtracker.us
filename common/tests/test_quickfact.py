from django.test import TestCase

from common.tests.factories import CategoryPageFactory
from common.models.pages import QuickFact


class CleanTest(TestCase):
    def test_should_unescape_html_entities_in_tags(self):
        category = CategoryPageFactory()
        fact = QuickFact(
            page=category,
            body='<p>{% num_targets categories=10 date_lower=&quot;2019-01-01&quot; %} journalists ate broccoli in 2019</p>'
        )
        fact.clean()
        self.assertEqual(
            fact.body,
            '<p>{% num_targets categories=10 date_lower="2019-01-01" %} journalists ate broccoli in 2019</p>'
        )
