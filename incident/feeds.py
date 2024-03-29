import re
from urllib.parse import urljoin

from django.core.paginator import Paginator
from django.contrib.syndication.views import Feed

from common.feeds import MRSSFeed


class IncidentIndexPageFeed(Feed):
    "A feed for IncidentPages that are children of an IncidentIndexPage"

    feed_type = MRSSFeed

    def __init__(self, incident_index_page, *args, **kwargs):
        self.incident_index_page = incident_index_page
        self.feed_per_page = self.incident_index_page.feed_per_page
        super(IncidentIndexPageFeed, self).__init__(*args, **kwargs)

    def _get_teaser_image(self, obj):
        if obj.teaser_image:
            return obj.teaser_image.get_rendition('original')

    def _get_categories(self, obj):
        categories = obj.categories.all().select_related('category')
        return [inline.category for inline in categories]

    def _get_complete_url(self, path):
        return urljoin(
            self.incident_index_page.get_site().root_url,
            path
        )

    def _get_cleaned_feed(self, text):
        # Strip control characters that return error from Django
        return re.sub(
            r'[\x00-\x08\x0B-\x0C\x0E-\x1F]',
            '',
            text
        )

    def get_object(self, request, *args, **kwargs):
        self.page = int(request.GET.get('p', 1))
        incidents = self.incident_index_page.get_incidents()

        if self.incident_index_page.feed_limit != 0:
            incidents = incidents[:self.incident_index_page.feed_limit]

        self.paginator = Paginator(incidents, self.feed_per_page)
        self.last_page = self.paginator.page_range.stop - 1
        return super(IncidentIndexPageFeed, self).get_object(request, *args, **kwargs)

    def title(self):
        return '{}: {}'.format(
            self.incident_index_page.get_site().site_name,
            self.incident_index_page.title
        )

    def link(self):
        return self._get_complete_url(self.incident_index_page.url)

    def description(self):
        return self.incident_index_page.search_description

    def feed_url(self):
        return self._get_complete_url(
            self.incident_index_page.url + self.incident_index_page.reverse_subpage('feed')
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
        return self._get_cleaned_feed(obj.title)

    def item_description(self, obj):
        return self._get_cleaned_feed(obj.body.render_as_block())

    def item_link(self, obj):
        return self._get_complete_url(obj.url)

    def item_guid(self, obj):
        return self.item_link(obj)

    item_guid_is_permalink = True

    def item_pubdate(self, obj):
        return obj.first_published_at

    def item_updatedate(self, obj):
        return obj.last_published_at

    def item_categories(self, obj):
        categories = self._get_categories(obj)
        return (category.title for category in categories)

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
