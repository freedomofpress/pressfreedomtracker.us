from django.test import TestCase

from common.templatetags.render_as_template import render_as_template


class StatisticsTest(TestCase):
    def test_loads_statistics(self):
        rendered = render_as_template('{% num_incidents %}')
        self.assertEqual(rendered, '0')
