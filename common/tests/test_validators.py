from django.core.exceptions import ValidationError
from django.test import TestCase

from common.validators import validate_disallow_comma


class TestValidateCommaDisallowed(TestCase):
    def test_raise_error_when_comma_in_disallowed_field(self):
        with self.assertRaises(ValidationError):
            validate_disallow_comma('Hello, world')
