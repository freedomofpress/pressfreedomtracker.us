from mimetypes import guess_type
from django.contrib.syndication.views import Feed


class IncidentIndexPageFeed(Feed):
    "A feed for IncidentPages that are children of an IncidentIndexPage"

    def __init__(self, incident_index_page, *args, **kwargs):
        self.incident_index_page = incident_index_page
        super(IncidentIndexPageFeed, self).__init__(*args, **kwargs)

    def _get_categories(self, obj):
        return [inline.category for inline in obj.categories.all().select_related('category')]

    def _get_teaser_image(self, obj):
        if obj.teaser_image:
            return obj.teaser_image.get_rendition('original')

    def _get_complete_url(self, obj, path):
        return '{}{}'.format(
            obj.get_site().root_url,
            path
        )

    def title(self):
        return self.title

    def link(self):
        return self.incident_index_page.url

    def description(self):
        return self.incident_index_page.search_description

    def items(self):
        incidents = self.incident_index_page.get_incidents()

        if self.incident_index_page.feed_limit != 0:
            return incidents[:self.incident_index_page.feed_limit]

        return incidents

    def item_title(self, obj):
        return obj.title

    def item_description(self, obj):
        return obj.body.render_as_block()

    def item_link(self, obj):
        return self._get_complete_url(obj, obj.url)

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

    def item_enclosure_url(self, obj):
        image = self._get_teaser_image(obj)
        return self._get_complete_url(obj, image.url) if image else None

    def item_enclosure_length(self, obj):
        image = self._get_teaser_image(obj)
        return image.file.size

    def item_enclosure_mime_type(self, obj):
        image = self._get_teaser_image(obj)
        return guess_type(image.url)[0]
