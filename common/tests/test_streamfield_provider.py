from django.test import TestCase

from faker import Faker

from common.tests.utils import StreamfieldFieldError, StreamfieldProvider


class TestStreamfieldProvider(TestCase):
    def setUp(self):
        self.fake = Faker()
        self.fake.add_provider(StreamfieldProvider)

    def test_raises_if_no_fields_given(self):
        with self.assertRaises(StreamfieldFieldError):
            self.fake.streamfield(fields=[])

    def test_raises_if_unknown_field_given(self):
        with self.assertRaises(StreamfieldFieldError):
            self.fake.streamfield(fields=["not_a_real_field"])
