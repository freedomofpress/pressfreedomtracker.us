from django.test import TestCase

from common.blocks import AlignedCaptionedImageBlock
from common.tests.factories import AlignedCaptionedImageBlockFactory


class AlignedCaptionedImageBlockGetContextTest(TestCase):
    def test_get_context_with_content_warning_unwraps_first_item(self):
        block = AlignedCaptionedImageBlock()
        value = AlignedCaptionedImageBlockFactory()
        value['content_warning'] = ['This image may be disturbing.']

        block.get_context(value)

        self.assertEqual(value['content_warning'], 'This image may be disturbing.')

    def test_get_context_without_content_warning_leaves_value_unchanged(self):
        block = AlignedCaptionedImageBlock()
        value = AlignedCaptionedImageBlockFactory()
        value['content_warning'] = []

        block.get_context(value)

        self.assertEqual(value['content_warning'], [])
