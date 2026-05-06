from django.test import TestCase

from common.blocks import AlignedCaptionedImageBlock


class AlignedCaptionedImageBlockGetContextTest(TestCase):
    def test_get_context_with_content_warning_unwraps_first_item(self):
        warning_text = "This image may be disturbing."
        block = AlignedCaptionedImageBlock()
        value = block.to_python(
            {
                "content_warning": [warning_text],
            }
        )
        block.get_context(value)
        self.assertEqual(value["content_warning"], warning_text)

    def test_get_context_without_content_warning_leaves_value_unchanged(self):
        block = AlignedCaptionedImageBlock()
        value = block.to_python(
            {
                "content_warning": [],
            }
        )

        block.get_context(value)
        self.assertEqual(list(value["content_warning"]), [])
