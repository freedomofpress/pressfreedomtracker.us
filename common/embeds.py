import re

from django.template.loader import render_to_string

from wagtail.embeds.finders.base import EmbedFinder


# Instagram URL matcher that will match a URL to a post with or without a trailing
# slash. The capture group lets us strip any querystring parameters we might be
# given.
INSTAGRAM_URL_RE = re.compile(r'(https?://(www\.)?instagram\.com/p/[\w-]+)/?')


class InstagramEmbedFinder(EmbedFinder):
    def accept(self, url):
        return bool(INSTAGRAM_URL_RE.match(url))

    def find_embed(self, url, max_width=None, max_height=None):
        # Get the match group as the URL to avoid querystring parameters. The group
        # should be present because find_embed is called after accept() validation.
        clean_url = INSTAGRAM_URL_RE.match(url).group(1)
        html = render_to_string('common/embeds/instagram.html', {
            'url': clean_url,
        })
        return {
            'provider_name': 'Instagram',
            'type': 'rich',
            'html': html,
            'width': max_width,
            'height': max_height,
        }
