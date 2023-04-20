from django.test import TestCase

from common.models import helpers

from .factories import CommonTagFactory


class TestGetTags(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tags = CommonTagFactory.create_batch(3)

    def test_get_tag_returns_tags_as_choices(self):
        self.assertEqual(
            helpers.get_tags(),
            [(tag.title, tag.title) for tag in self.tags]
        )
