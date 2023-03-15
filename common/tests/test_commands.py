import os
from unittest import mock

import wagtail_factories
from django.core import management
from django.test import TestCase

from common.management.commands.createdevdata import Command


class CreateDevDataTestCase(TestCase):

    def test_createdevdata_works(self):
        """The createdevdata command successfully creates pages"""
        # Write stdout to /dev/null so as not to clutter the output from the tests
        with open(os.devnull, 'w') as devnull:
            management.call_command('createdevdata', '--no-download', stdout=devnull)

    @mock.patch('requests.get')
    def test_createdevdata_fetch_images(self, mock_requests):
        mock_response = mock_requests.return_value
        mock_response.content = ''
        photo_collection = wagtail_factories.CollectionFactory(name='Photos')
        Command().fetch_image(200, 200, photo_collection)
        self.assertEqual(mock_requests.call_args.kwargs['timeout'], 5)
