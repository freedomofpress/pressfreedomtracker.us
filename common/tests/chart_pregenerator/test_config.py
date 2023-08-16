from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings, TestCase

from common.utils.chart_pregenerator.config import Settings


class TestConfig(TestCase):
    @override_settings(CHART_PREGENERATOR={})
    def test_no_config(self):
        with self.assertRaises(ImproperlyConfigured):
            Settings().validate()

    @override_settings(CHART_PREGENERATOR={'HOST': 'chartgen'})
    def test_no_port(self):
        with self.assertRaisesRegex(ImproperlyConfigured, 'PORT must be an integer'):
            Settings().validate()

    @override_settings(CHART_PREGENERATOR={'HOST': 'chartgen', 'PORT': 'abc'})
    def test_noninteger_port(self):
        with self.assertRaisesRegex(ImproperlyConfigured, 'PORT must be an integer'):
            Settings().validate()

    @override_settings(CHART_PREGENERATOR={'PORT': 3000})
    def test_no_host(self):
        with self.assertRaisesRegex(ImproperlyConfigured, 'HOST must be a string'):
            Settings().validate()

    @override_settings(CHART_PREGENERATOR={
        'HOST': 'chartgen',
        'PORT': 3000,
    })
    def test_valid_settings(self):
        s = Settings()
        s.validate()
        self.assertEqual(s.host, 'chartgen')
        self.assertEqual(s.port, 3000)
