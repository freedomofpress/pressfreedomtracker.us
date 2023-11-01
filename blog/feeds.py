from urllib.parse import urljoin
from collections import namedtuple
from django.core.paginator import Paginator
from django.contrib.syndication.views import Feed

from common.feeds import MRSSFeed


class BlogIndexPageFeed(Feed):
    "A feed for BlogPages that are children of a BlogIndexPage"

    feed_type = MRSSFeed

    def __init__(self, blog_index_page, *args, **kwargs):
        self.blog_index_page = blog_index_page
        self.feed_per_page = self.blog_index_page.feed_per_page
        super(BlogIndexPageFeed, self).__init__(*args, **kwargs)

    def _get_teaser_image(self, obj):
        try:
            teaser_block = obj.teaser_graphic[0]
            if teaser_block.block_type == "image":
                return teaser_block.value.get_rendition('original')
            elif teaser_block.block_type in (
                "vertical_bar_chart",
                "tree_map_chart",
                "bubble_map_chart",
            ):
                teaser_svg = namedtuple('teaser_svg', 'url width height')
                return teaser_svg(
                    url=teaser_block.value.svg_snapshot_mini_datauri(),
                    width=655,
                    height=440,
                )
        except IndexError:
            pass

    def _get_categories(self, obj):
        categories = obj.categories.all().select_related('category')
        return [inline.category for inline in categories]

    def _get_complete_url(self, path):
        return urljoin(
            self.blog_index_page.get_site().root_url,
            path
        )

    def get_object(self, request, *args, **kwargs):
        self.page = int(request.GET.get('p', 1))
        posts = self.blog_index_page.get_posts()

        if self.blog_index_page.feed_limit != 0:
            posts = posts[:self.blog_index_page.feed_limit]

        self.paginator = Paginator(posts, self.feed_per_page)
        self.last_page = self.paginator.page_range.stop - 1
        return super(BlogIndexPageFeed, self).get_object(request, *args, **kwargs)

    def title(self):
        return '{}: {}'.format(
            self.blog_index_page.get_site().site_name,
            self.blog_index_page.title
        )

    def link(self):
        return self._get_complete_url(self.blog_index_page.url)

    def description(self):
        return self.blog_index_page.search_description

    def feed_url(self):
        return self._get_complete_url(
            self.blog_index_page.url + self.blog_index_page.reverse_subpage('feed')
        )

    def feed_guid(self):
        return self.feed_url()

    def feed_extra_kwargs(self, obj):
        return {
            'page': self.page,
            'last_page': self.last_page,
        }

    def items(self):
        return self.paginator.get_page(self.page)

    def item_title(self, obj):
        return obj.title

    def item_description(self, obj):
        return obj.body.render_as_block()

    def item_link(self, obj):
        return self._get_complete_url(obj.url)

    def item_guid(self, obj):
        return self.item_link(obj)

    item_guid_is_permalink = True

    def item_pubdate(self, obj):
        return obj.first_published_at

    def item_updatedate(self, obj):
        return obj.last_published_at

    def item_extra_kwargs(self, obj):
        image = self._get_teaser_image(obj)
        if image:
            return {
                'teaser_image': {
                    'url': image.url,
                    'width': image.width,
                    'height': image.height,
                }
            }
        return {}
