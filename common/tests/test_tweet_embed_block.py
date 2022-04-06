from django.core.exceptions import ValidationError
from django.test import TestCase
from wagtail.embeds.blocks import EmbedValue

from common.blocks import TweetEmbedBlock


class CleanTest(TestCase):
    def test_clean_non_twitter_url(self):
        block = TweetEmbedBlock()
        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'tweet': EmbedValue('https://youtu.be/C0DPdy98e4c'),
            })

        self.assertEqual(cm.exception.params, {'tweet': ['Please enter a valid Twitter URL.']})

    def test_clean_http_www_twitter_url(self):
        block = TweetEmbedBlock()
        with self.assertRaises(ValidationError) as cm:
            block.clean({
                'tweet': EmbedValue('http://www.twitter.com/WagtailCMS/status/1413141835711606786'),
            })

        self.assertEqual(cm.exception.params, {'tweet': ['Please enter a valid Twitter URL.']})

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

        self.assertEqual(cm.exception.params, {'tweet': ['Please enter a valid Twitter URL.']})

    def test_clean_https_naked_twitter_url(self):
        block = TweetEmbedBlock()
        cleaned_value = block.clean({
            'tweet': EmbedValue('https://twitter.com/WagtailCMS/status/1413141835711606786'),
        })

        self.assertEqual(cleaned_value['tweet'].url,
                         'https://twitter.com/WagtailCMS/status/1413141835711606786')
