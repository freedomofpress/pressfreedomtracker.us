from html import unescape

from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.html import strip_tags
from django.template.defaultfilters import truncatewords

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
    InlinePanel,
)
from wagtail import blocks
from wagtail.fields import StreamField, RichTextField
from wagtail.models import Page, Orderable
from wagtail.permission_policies.base import ModelPermissionPolicy
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail_newsletter.models import NewsletterPageMixin

from common.utils import DEFAULT_PAGE_KEY, paginate
from common.exceptions import ChartNotAvailable

from blog.choices import BlogTemplateType
from blog.feeds import BlogIndexPageFeed
from blog.utils import BlogFilter
from statistics.blocks import StatisticsBlock
from common.models import (
    PersonPage,
    OrganizationPage,
    MetadataPageMixin,
    MediaPageMixin,
)
from common.blocks import (
    BlueskyEmbedBlock,
    Heading1,
    Heading2,
    Heading3,
    InstagramEmbedBlock,
    StyledTextBlock,
    AlignedCaptionedImageBlock,
    AlignedCaptionedEmbedBlock,
    TweetEmbedBlock,
    RichTextBlockQuoteBlock,
    AsideBlock,
    ButtonBlock,
    VerticalBarChart,
    TreeMapChart,
    BubbleMapChart,
    HexbinMapChart,
)


class BlogIndexPage(RoutablePageMixin, MetadataPageMixin, MediaPageMixin, Page):
    body = StreamField(
        [
            ("rich_text", blocks.RichTextBlock(icon="doc-full", label="Rich Text")),
            ("image", ImageChooserBlock()),
            ("raw_html", blocks.RawHTMLBlock()),
            ("tweet", TweetEmbedBlock(group="Social Media")),
            ("instagram", InstagramEmbedBlock(group="Social Media")),
            ("bluesky", BlueskyEmbedBlock(group="Social Media")),
        ],
        use_json_field=True,
    )

    newsletter_preamble = RichTextField(
        blank=True,
        null=True,
        help_text="Newsletter preamble that appears at the top of a newsletter before the newsletter image.",
    )

    about_blog_title = models.CharField(max_length=255, blank=True, null=True)
    feed_limit = models.PositiveIntegerField(
        default=20,
        help_text="Maximum number of posts to be included in the "
        "syndication feed. 0 for unlimited.",
    )
    feed_per_page = models.PositiveIntegerField(
        default=20,
        help_text="Maximum number of posts to be included per page "
        "in the syndication feed.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        InlinePanel(
            "featured_blogs",
            label="Featured Blogs",
            min_num=3,
            max_num=6,
        ),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel("about_blog_title"),
        FieldPanel("feed_limit"),
        FieldPanel("feed_per_page"),
        MultiFieldPanel(
            children=[
                FieldPanel("newsletter_preamble"),
            ],
            heading="Newsletter Campaign Settings",
        ),
    ]

    subpage_types = ["blog.BlogPage"]

    @path("feed/")
    def feed(self, request):
        return BlogIndexPageFeed(self)(request)

    def get_posts(self):
        return BlogPage.objects.child_of(self).live().order_by("-publication_datetime")

    def get_context(self, request, *args, **kwargs):
        context = super(BlogIndexPage, self).get_context(request, *args, **kwargs)

        post_filters = BlogFilter.from_querystring(request.GET)
        entry_qs = post_filters.filter(self.get_posts())

        if request.GET.get("author"):
            author_filter = get_object_or_404(PersonPage, pk=post_filters.author)
        if request.GET.get("organization"):
            organization_filter = get_object_or_404(
                OrganizationPage, pk=post_filters.organization
            )

        paginator, entries = paginate(
            request, entry_qs, page_key=DEFAULT_PAGE_KEY, per_page=8, orphans=5
        )

        context["type_choices"] = [
            (BlogTemplateType.DEFAULT, "Articles"),
            (BlogTemplateType.SPECIAL, "Special Sections"),
            (BlogTemplateType.NEWSLETTER, "Newsletters"),
        ]
        context["post_filters"] = post_filters
        context["entries_page"] = entries
        context["paginator"] = paginator

        if not request.GET.get("author") and not request.GET.get("organization"):
            context["featured_blogs"] = [
                f.page
                for f in self.featured_blogs.select_related("page").all()
                if f.page_id
            ]

        context["incident_listing_heading"] = "Latest"
        if request.GET.get("author"):
            context["incident_listing_heading"] = (
                f"Showing posts by <b>{author_filter.title}</b>"
            )
        if request.GET.get("organization"):
            context["incident_listing_heading"] = (
                f"Showing posts by <b>{organization_filter.title}</b>"
            )

        return context

    def get_cache_tag(self):
        return "blog-index-{}".format(self.pk)

    # The following method is in large part copied from incident_index_page.py.
    def serve(self, request, *args, **kwargs):
        response = super(BlogIndexPage, self).serve(request, *args, **kwargs)

        # We set a cache tag here so that elsewhere we can purge all subroutes
        # of the blog (including paginated and filtered URLs) simultaneously
        response["Cache-Tag"] = self.get_cache_tag()
        return response

    def get_meta_description(self):
        return truncatewords(strip_tags(self.body.render_as_block()), 20)


class BlogIndexPageFeature(Orderable):
    blog_index_page = ParentalKey("blog.BlogIndexPage", related_name="featured_blogs")
    page = models.ForeignKey("blog.BlogPage", on_delete=models.CASCADE)

    panels = [
        FieldPanel("page"),
    ]


class BlogAuthor(Orderable):
    parent_page = ParentalKey("BlogPage", related_name="authors")
    author = models.ForeignKey(
        "common.PersonPage", on_delete=models.CASCADE, related_name="+"
    )

    @property
    def summary(self):
        return self.author.title

    panels = [FieldPanel("author")]


class BlogPage(NewsletterPageMixin, MetadataPageMixin, MediaPageMixin, Page):
    publication_datetime = models.DateTimeField(
        help_text="Past or future date of publication",
        null=True,
    )

    blog_type = models.CharField(
        max_length=20,
        choices=BlogTemplateType.choices,
        default=BlogTemplateType.DEFAULT,
        help_text="Select template used to display this post.",
    )

    body = StreamField(
        [
            (
                "text",
                StyledTextBlock(
                    label="Text", template="common/blocks/styled_text_full_bleed.html"
                ),
            ),
            ("aside", AsideBlock()),
            ("image", AlignedCaptionedImageBlock()),
            ("raw_html", blocks.RawHTMLBlock()),
            ("tweet", TweetEmbedBlock(group="Social Media")),
            ("instagram", InstagramEmbedBlock(group="Social Media")),
            ("bluesky", BlueskyEmbedBlock(group="Social Media")),
            ("blockquote", RichTextBlockQuoteBlock()),
            (
                "list",
                blocks.ListBlock(
                    blocks.CharBlock(label="List Item"),
                    template="common/blocks/list_block_columns.html",
                ),
            ),
            ("video", AlignedCaptionedEmbedBlock()),
            ("heading_1", Heading1()),
            ("heading_2", Heading2()),
            ("heading_3", Heading3()),
            ("button", ButtonBlock()),
            ("statistics", StatisticsBlock()),
            ("vertical_bar_chart", VerticalBarChart(group="Charts")),
            ("tree_map_chart", TreeMapChart(group="Charts")),
            ("bubble_map_chart", BubbleMapChart(group="Charts")),
            ("hexbin_map_chart", HexbinMapChart(group="Charts")),
        ],
        use_json_field=True,
    )

    newsletter_preamble = RichTextField(
        blank=True,
        null=True,
        verbose_name="Newsletter preamble override",
        help_text="Overrides the newsletter preamble set in the Blog Index Page for this specific Blog Page.",
    )

    hide_newsletter_web_link = models.BooleanField(
        default=False,
        verbose_name="Hide “View this newsletter on pressfreedomtracker.us” banner",
        help_text="Check this if the page is never intended to be published.",
    )

    introduction = models.TextField(
        help_text="Optional: introduction displayed above the image/video.",
        blank=True,
        null=True,
    )

    link_to_original_post = models.URLField(blank=True)

    lead_graphic = StreamField(
        [
            ("image", ImageChooserBlock()),
            ("vertical_bar_chart", VerticalBarChart()),
            ("tree_map_chart", TreeMapChart()),
            ("bubble_map_chart", BubbleMapChart()),
            ("hexbin_map_chart", HexbinMapChart()),
        ],
        use_json_field=True,
        blank=True,
        default=[],
        max_num=1,
    )

    teaser_graphic = StreamField(
        [
            ("image", ImageChooserBlock()),
            ("vertical_bar_chart", VerticalBarChart()),
            ("tree_map_chart", TreeMapChart()),
            ("bubble_map_chart", BubbleMapChart()),
            ("hexbin_map_chart", HexbinMapChart()),
        ],
        use_json_field=True,
        blank=True,
        default=[],
        max_num=1,
    )

    # Note: The following fields are deprecated in favor for lead_graphic and teaser_graphic,
    # and will be removed in a future version
    lead_image = models.ForeignKey(
        "common.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    teaser_image = models.ForeignKey(
        "common.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    image_caption = RichTextField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Image description displayed below the lead image. Organization/Photographer can be set via the image attribution.",
    )

    teaser_text = models.TextField(null=True, blank=True)

    organization = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blog_posts",
    )

    content_panels = Page.content_panels + [
        FieldPanel("publication_datetime"),
        FieldPanel("newsletter_preamble"),
        FieldPanel("body"),
        FieldPanel("link_to_original_post"),
        MultiFieldPanel(
            heading="Introduction",
            children=[
                FieldPanel("introduction"),
                FieldPanel("lead_graphic"),
                FieldPanel("image_caption"),
            ],
        ),
        MultiFieldPanel(
            heading="Teaser",
            children=[
                FieldPanel("teaser_graphic"),
                FieldPanel("teaser_text"),
            ],
        ),
        PageChooserPanel("organization", "common.OrganizationPage"),
        InlinePanel(
            "authors", label="Authors", help_text="Author pages must already exist."
        ),
    ]

    settings_panels = Page.settings_panels + [FieldPanel("blog_type")]

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []
    newsletter_template = "blog/blog_page_newsletter.html"

    class Meta:
        permissions = [
            ("save_campaign_blogpage", "Can save campaign"),
            ("send_test_email_blogpage", "Can send test email"),
            ("send_campaign_blogpage", "Can send campaign"),
            ("schedule_campaign_blogpage", "Can schedule campaign"),
            ("unschedule_campaign_blogpage", "Can unschedule campaign"),
            ("get_report_blogpage", "Can get report"),
            ("access_newsletter_tab_blogpage", "Can access newsletter tab"),
        ]

    def has_newsletter_permission(self, user, action):
        permission_policy = ModelPermissionPolicy(type(self))
        return permission_policy.user_has_permission(user, action)

    @classmethod
    def get_newsletter_panels(cls):
        panels = [panel.clone() for panel in super().get_newsletter_panels()]
        # Place hide web link checkbox at end of list but above send buttons.
        panels.insert(-1, FieldPanel("hide_newsletter_web_link"))
        for panel in panels:
            panel.permission = "blog.access_newsletter_tab_blogpage"
        return panels

    def get_base_url(self):
        return self.get_site().root_url

    def get_newsletter_preamble(self):
        # If newsletter preamble is set in the individual blog page
        # that value is used and overrides the blog index page value,
        # else, use blog index page newsletter preamble
        if self.newsletter_preamble:
            return self.newsletter_preamble
        parent = self.get_parent().specific
        return parent.newsletter_preamble

    def get_newsletter_preview_text(self):
        # Plain-text teaser for the email preheader (mj-preview)
        preamble = self.get_newsletter_preamble()
        if preamble:
            return unescape(strip_tags(preamble)).strip()
        for block in self.body:
            if block.block_type == "text":
                # Body text isn't written as a teaser, so cap the fallback.
                text = unescape(strip_tags(str(block.value["text"]))).strip()
                return truncatewords(text, 30)
        return ""

    def get_meta_image(self):
        if (
            self.teaser_graphic
            and self.teaser_graphic[0]
            and self.teaser_graphic[0].block_type == "image"
        ):
            return self.teaser_graphic[0].value

        if (
            self.teaser_graphic
            and self.teaser_graphic[0]
            and self.teaser_graphic[0].block_type
            in (
                "vertical_bar_chart",
                "tree_map_chart",
                "bubble_map_chart",
            )
        ):
            try:
                return self.teaser_graphic[0].value.png_snapshot_meta()
            except ChartNotAvailable:
                pass
        return super(BlogPage, self).get_meta_image()

    def get_meta_description(self):
        if self.teaser_text:
            return self.teaser_text

        if self.search_description:
            return self.search_description

        return truncatewords(
            strip_tags(self.body.render_as_block()), 20
        )  # pragma: no cover
