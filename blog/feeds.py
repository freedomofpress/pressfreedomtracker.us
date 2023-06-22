from urllib.parse import urljoin

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
        if obj.teaser_graphic:
            return obj.teaser_graphic.get_rendition('original')

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
                    'url': self._get_complete_url(image.url),
                    'width': image.width,
                    'height': image.height,
                }
            }
        return {}
