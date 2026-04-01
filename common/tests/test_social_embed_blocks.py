from django.core.exceptions import ValidationError
from django.test import TestCase
from wagtail.embeds.blocks import EmbedValue

from common.blocks import InstagramEmbedBlock, TweetEmbedBlock


class CleanTest(TestCase):
    def test_clean_non_twitter_url(self):
        block = TweetEmbedBlock()
        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'tweet': EmbedValue('https://youtu.be/C0DPdy98e4c'),
            })

        self.assertEqual(cm.exception.block_errors, {'tweet': ValidationError('Please enter a valid Twitter URL.')})

    def test_clean_http_www_twitter_url(self):
        block = TweetEmbedBlock()
        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'tweet': EmbedValue('http://www.twitter.com/WagtailCMS/status/1413141835711606786'),
            })
        self.assertEqual(cm.exception.block_errors, {'tweet': ValidationError('Please enter a valid Twitter URL.')})

    def test_clean_http_naked_twitter_url(self):
        block = TweetEmbedBlock()
        cleaned_value = block.clean({
            'tweet': EmbedValue('http://twitter.com/WagtailCMS/status/1413141835711606786'),
        })

        self.assertEqual(cleaned_value['tweet'].url,
                         'http://twitter.com/WagtailCMS/status/1413141835711606786')

    def test_clean_https_www_twitter_url(self):
        block = TweetEmbedBlock()
        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'tweet': EmbedValue('https://www.twitter.com/WagtailCMS/status/1413141835711606786'),
            })

        self.assertEqual(cm.exception.block_errors, {'tweet': ValidationError('Please enter a valid Twitter URL.')})

    def test_clean_https_naked_twitter_url(self):
        block = TweetEmbedBlock()
        cleaned_value = block.clean({
            'tweet': EmbedValue('https://twitter.com/WagtailCMS/status/1413141835711606786'),
        })

        self.assertEqual(cleaned_value['tweet'].url,
                         'https://twitter.com/WagtailCMS/status/1413141835711606786')

    def test_clean_https_naked_x_url(self):
        block = TweetEmbedBlock()

        cleaned_value = block.clean({
            'tweet': EmbedValue('https://x.com/WagtailCMS/status/1413141835711606786'),
        })
        self.assertEqual(cleaned_value['tweet'].url,
                         'https://x.com/WagtailCMS/status/1413141835711606786')

    def test_validate_instagram_url_valid(self):
        block = InstagramEmbedBlock()
        cleaned_value = block.clean({
            'url': 'https://instagram.com/p/C0DPdy98e4c',
        })
        self.assertEqual(cleaned_value['url'], 'https://instagram.com/p/C0DPdy98e4c')

    def test_validate_instagram_url_with_www(self):
        block = InstagramEmbedBlock()
        cleaned_value = block.clean({
            'url': 'https://www.instagram.com/p/C0DPdy98e4c',
        })
        self.assertEqual(cleaned_value['url'], 'https://www.instagram.com/p/C0DPdy98e4c')

    def test_validate_instagram_url_non_instagram(self):
        block = InstagramEmbedBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'url': 'https://twitter.com/WagtailCMS/status/1413141835711606786',
            })

    def test_validate_instagram_url_empty_string(self):
        block = InstagramEmbedBlock()
        with self.assertRaises(ValidationError):
            block.clean({
                'url': '',
            })
