from django.test import TestCase

from common.embeds import InstagramEmbedFinder


class InstagramEmbedFinderTests(TestCase):

    def setUp(self):
        self.finder = InstagramEmbedFinder()

    def test_regex_accepts_standard_post_urls(self):
        self.assertTrue(self.finder.accept('https://www.instagram.com/p/ABC123/'))
        self.assertTrue(self.finder.accept('https://instagram.com/p/ABC123'))

    def test_regex_rejects_non_post_urls(self):
        self.assertFalse(
            self.finder.accept('https://www.instagram.com/freedomofthepressfoundation/')
        )
        self.assertFalse(
            self.finder.accept('https://bsky.app/profile/freedom.press/post/ABC123/')
        )

    def test_find_embed_html_contains_post_url(self):
        result = self.finder.find_embed('https://www.instagram.com/p/ABC123/')
        self.assertIn('instagram.com/p/ABC123', result['html'])

    def test_find_embed_html_cleans_url(self):
        # And make sure it strips given querystring args
        result = self.finder.find_embed(
            'https://www.instagram.com/p/ABC123/??utm_source=ig_web_copy_link'
        )
        self.assertNotIn('ig_web_copy_link', result['html'])
