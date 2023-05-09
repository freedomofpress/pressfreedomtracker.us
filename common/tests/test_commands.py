import os
from unittest import mock

import wagtail_factories
from django.core import management
from django.test import TestCase

from common.devdata import CustomImageFactory
from common.management.commands.createdevdata import Command
from blog.devdata import BlogPageFactory
from incident.devdata import MultimediaIncidentPageFactory


class CreateDevDataTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Seed the db with images.  This is a workaround for
        # `factory.Iterator`, used by BlogPageFactory and
        # MultimediaIncidentPageFactory, to function across multiple
        # test cases.  Normally these images would be made by the
        # `createdevdata` command itself.  But it seems like the
        # _second_ time we run the command, the images are created
        # with database ID values not starting at 1, since the
        # database's sequence counter is not reset between tests.
        # This seems to confuse the `Iterator`, which goes back to
        # looking for an object with ID 1.  This ensures that we have
        # enough images at the start of the sequence so that the
        # command can fully run.
        CustomImageFactory.create_batch(
            50,
            file__width=1,
            file__height=1,
            file__color='red',
            collection__name='Photos',
        )

    def setUp(self):
        # Reset iterator counters to ensure they are able to find one
        # of the above images across all tests.
        BlogPageFactory.teaser_image.reset()
        MultimediaIncidentPageFactory.teaser_image.reset()

    def test_createdevdata_works(self):
        """The createdevdata command successfully creates pages"""
        # Write stdout to /dev/null so as not to clutter the output from the tests
        with open(os.devnull, 'w') as devnull:
            management.call_command(
                'createdevdata',
                '--no-download',
                '--max-incidents=25',
                stdout=devnull,
            )

    def test_createdevdata_geolocated(self):
        with open(os.devnull, 'w') as devnull:
            management.call_command(
                'createdevdata',
                '--no-download',
                '--geolocated',
                '--max-incidents=3',
                stdout=devnull,
            )

    @mock.patch('requests.get')
    def test_createdevdata_fetch_images(self, mock_requests):
        mock_response = mock_requests.return_value
        mock_response.content = ''
        photo_collection = wagtail_factories.CollectionFactory(name='Photos')
        Command().fetch_image(200, 200, photo_collection)
        self.assertEqual(mock_requests.call_args.kwargs['timeout'], 5)
