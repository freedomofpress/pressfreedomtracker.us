from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.cache import patch_cache_control
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
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.routable_page.models import RoutablePageMixin, path

from common.utils import DEFAULT_PAGE_KEY, paginate

from blog.feeds import BlogIndexPageFeed
from blog.utils import BlogFilter
from statistics.blocks import StatisticsBlock
from common.models import PersonPage, OrganizationPage, MetadataPageMixin, MediaPageMixin
from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
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
)


class BlogIndexPage(RoutablePageMixin, MetadataPageMixin, Page):
    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('tweet', TweetEmbedBlock())
    ], use_json_field=True)

    about_blog_title = models.CharField(max_length=255, blank=True, null=True)
    feed_limit = models.PositiveIntegerField(
        default=20,
        help_text='Maximum number of posts to be included in the '
                  'syndication feed. 0 for unlimited.'
    )
    feed_per_page = models.PositiveIntegerField(
        default=20,
        help_text='Maximum number of posts to be included per page '
                  'in the syndication feed.'
    )

    content_panels = Page.content_panels + [
        FieldPanel('body'),
        InlinePanel(
            'featured_blogs',
            label='Featured Blogs',
            min_num=3,
            max_num=6,
        ),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('about_blog_title'),
        FieldPanel('feed_limit'),
        FieldPanel('feed_per_page'),
    ]

    subpage_types = ['blog.BlogPage']

    @path('feed/')
    def feed(self, request):
        return BlogIndexPageFeed(self)(request)

    def get_posts(self):
        return BlogPage.objects.child_of(self)\
                       .live()\
                       .order_by('-publication_datetime')

    def get_context(self, request, *args, **kwargs):
        context = super(BlogIndexPage, self).get_context(request, *args, **kwargs)

        post_filters = BlogFilter.from_querystring(request.GET)
        entry_qs = post_filters.filter(self.get_posts())

        if request.GET.get('author'):
            author_filter = get_object_or_404(PersonPage, pk=post_filters.author)
        if request.GET.get('organization'):
            organization_filter = get_object_or_404(OrganizationPage, pk=post_filters.organization)

        paginator, entries = paginate(
            request,
            entry_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=8,
            orphans=5
        )

        context['entries_page'] = entries
        context['paginator'] = paginator

        if not request.GET.get('author') and not request.GET.get('organization'):
            context['featured_blogs'] = [
                f.page for f in self.featured_blogs.select_related('page').all()
            ]

        context['incident_listing_heading'] = 'Latest'
        if request.GET.get('author'):
            context['incident_listing_heading'] = f'Showing posts by <b>{author_filter.title}</b>'
        if request.GET.get('organization'):
            context['incident_listing_heading'] = f'Showing posts by <b>{organization_filter.title}</b>'

        return context

    def get_cache_tag(self):
        return 'blog-index-{}'.format(self.pk)

    # The following method is in large part copied from incident_index_page.py.
    def serve(self, request, *args, **kwargs):
        response = super(BlogIndexPage, self).serve(request, *args, **kwargs)

        # We set a cache tag here so that elsewhere we can purge all subroutes
        # of the blog (including paginated and filtered URLs) simultaneously
        response['Cache-Tag'] = self.get_cache_tag()

        if request.is_ajax():
            # We don't want the browser to cache the response to an XHR because
            # it gets served with a different layout template. This becomes
            # problematic when a visitor hits the Back button in her browser
            # and ends up seeing the cached version without any typical layout.
            #
            # n.b. This method mutates the response and returns None.
            patch_cache_control(
                response,
                no_cache=True,
                no_store=True,
                must_revalidate=True,
            )
        return response

    def get_meta_description(self):
        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )


class BlogIndexPageFeature(Orderable):
    blog_index_page = ParentalKey('blog.BlogIndexPage', related_name='featured_blogs')
    page = models.ForeignKey('blog.BlogPage', on_delete=models.CASCADE)

    panels = [
        FieldPanel('page'),
    ]


class BlogPage(MetadataPageMixin, MediaPageMixin, Page):
    DEFAULT = 'default'
    NEWSLETTER = 'newsletter'
    SPECIAL = 'special'
    BLOG_TEMPLATE_CHOICES = (
        (DEFAULT, 'Default Blog'),
        (NEWSLETTER, 'Newsletter'),
        (SPECIAL, 'Special Blog'),
    )

    publication_datetime = models.DateTimeField(
        help_text='Past or future date of publication'
    )

    blog_type = models.CharField(
        max_length=20,
        choices=BLOG_TEMPLATE_CHOICES,
        default=DEFAULT,
        help_text='Select template used to display this post.',
    )

    body = StreamField([
        ('text', StyledTextBlock(label='Text', template='common/blocks/styled_text_full_bleed.html')),
        ('aside', AsideBlock()),
        ('image', AlignedCaptionedImageBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('tweet', TweetEmbedBlock()),
        ('blockquote', RichTextBlockQuoteBlock()),
        ('list', blocks.ListBlock(
            blocks.CharBlock(label="List Item"),
            template='common/blocks/list_block_columns.html'
        )),
        ('video', AlignedCaptionedEmbedBlock()),
        ('heading_1', Heading1()),
        ('heading_2', Heading2()),
        ('heading_3', Heading3()),
        ('button', ButtonBlock()),
        ('statistics', StatisticsBlock()),
        ('vertical_bar_chart', VerticalBarChart()),
        ('tree_map_chart', TreeMapChart()),
        ('bubble_map_chart', BubbleMapChart()),
    ], use_json_field=True)

    introduction = models.TextField(
        help_text="Optional: introduction displayed above the image/video.",
        blank=True,
        null=True,
    )

    link_to_original_post = models.URLField(blank=True)

    lead_image = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    teaser_image = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    image_caption = RichTextField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Image description displayed below the lead image. Organization/Photographer can be set via the image attribution.'
    )

    teaser_text = models.TextField(
        null=True,
        blank=True
    )

    organization = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_posts',
    )

    author = models.ForeignKey(
        # Likely a PersonPage
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content_panels = Page.content_panels + [
        FieldPanel('publication_datetime'),
        FieldPanel('body'),
        FieldPanel('link_to_original_post'),
        MultiFieldPanel(
            heading='Introduction',
            children=[
                FieldPanel('introduction'),
                FieldPanel('lead_image'),
                FieldPanel('image_caption'),
            ]
        ),
        MultiFieldPanel(
            heading='Teaser',
            children=[
                FieldPanel('teaser_image'),
                FieldPanel('teaser_text'),
            ]
        ),
        PageChooserPanel('organization', 'common.OrganizationPage'),
        PageChooserPanel('author', 'common.PersonPage'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('blog_type')
    ]

    parent_page_types = ['blog.BlogIndexPage']
    subpage_types = []

    def get_meta_image(self):
        return self.teaser_image or super(BlogPage, self).get_meta_image()

    def get_meta_description(self):
        if self.teaser_text:
            return self.teaser_text

        if self.search_description:
            return self.search_description

        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )
