from unittest import mock

from django.test import TestCase
import wagtail.embeds.exceptions
from common.templatetags.get_embed import get_embed


class TestGetEmbedTag(TestCase):
    @mock.patch("common.templatetags.get_embed.wagtail_get_embed")
    def test_returns_embed_object_on_success(self, mock_get_embed):
        fake_embed = mock.Mock()
        mock_get_embed.return_value = fake_embed

        result = get_embed("https://www.youtube.com/watch?v=abc123")

        mock_get_embed.assert_called_once_with("https://www.youtube.com/watch?v=abc123")
        self.assertEqual(result, fake_embed)

    @mock.patch("common.templatetags.get_embed.wagtail_get_embed")
    def test_returns_empty_string_on_embed_exception(self, mock_get_embed):
        mock_get_embed.side_effect = wagtail.embeds.exceptions.EmbedException()

        result = get_embed("https://www.youtube.com/watch?v=notfound")

        self.assertEqual(result, "")
