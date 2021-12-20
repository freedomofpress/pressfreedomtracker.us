from django.test import TestCase
from django.urls import reverse

from common.models import CustomImage, CustomRendition
from common.tests.factories import CustomImageFactory


class StyleguideTestCase(TestCase):
    def setUp(self):
        # Needed to supply the factory-generated Incident used to
        # render the styleguide with an image.
        CustomImageFactory.create(
            file__width=800,
            file__height=600,
            file__color='green',
            collection__name='Photos',
        )

    def tearDown(self):
        # Needed because the page the image is attached to is not
        # saved to the database, and the automatic teardown gets
        # confused by that when it attempts to enforce foreign key
        # constraints.
        CustomRendition.objects.all().delete()
        CustomImage.objects.all().delete()

    def test_styleguide_url_returns_200_status(self):
        self.response = self.client.get(reverse('styleguide'))
        self.assertEqual(self.response.status_code, 200)
