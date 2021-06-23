from django.utils.feedgenerator import Rss201rev2Feed


class MRSSFeed(Rss201rev2Feed):
    "Use Yahoo!'s MRSS spec to add thumbnail images to posts"

    def rss_attributes(self):
        attrs = super(MRSSFeed, self).rss_attributes()
        attrs['xmlns:dc'] = "http://purl.org/dc/elements/1.1/"
        attrs['xmlns:media'] = 'http://search.yahoo.com/mrss/'
        return attrs

    def add_item_elements(self, handler, item):
        super(MRSSFeed, self).add_item_elements(handler, item)
        if 'teaser_image' in item:
            handler.addQuickElement(
                'media:thumbnail',
                '',
                {
                    'url': item['teaser_image']['url'],
                    'width': str(item['teaser_image']['width']),
                    'height': str(item['teaser_image']['height']),
                }
            )

    def add_root_elements(self, handler):
        super(MRSSFeed, self).add_root_elements(handler)
        if self.feed["page"] is not None:
            if (
                self.feed["page"] >= 1
                and self.feed["page"] <= self.feed["last_page"]
            ):
                handler.addQuickElement(
                    "link",
                    "",
                    {
                        "rel": "first",
                        "href": f"{self.feed['feed_url']}?p=1",
                    },
                )
                handler.addQuickElement(
                    "link",
                    "",
                    {
                        "rel": "last",
                        "href": f"{self.feed['feed_url']}?p={self.feed['last_page']}",
                    },
                )
                if self.feed["page"] > 1:
                    handler.addQuickElement(
                        "link",
                        "",
                        {
                            "rel": "previous",
                            "href": f"{self.feed['feed_url']}?p={self.feed['page'] - 1}",
                        },
                    )
                if self.feed["page"] < self.feed["last_page"]:
                    handler.addQuickElement(
                        "link",
                        "",
                        {
                            "rel": "next",
                            "href": f"{self.feed['feed_url']}?p={self.feed['page'] + 1}",
                        },
                    )
