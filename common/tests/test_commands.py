import os

from django.core import management
from django.test import TestCase


class CreateDevDataTestCase(TestCase):

    def test_createdevdata_works(self):
        """The createdevdata command successfully creates pages"""
        # Write stdout to /dev/null so as not to clutter the output from the tests
        with open(os.devnull, 'w') as devnull:
            management.call_command('createdevdata', '--no-download', stdout=devnull)
