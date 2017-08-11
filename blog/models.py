from django.db import models
from django.utils.cache import patch_cache_control
from django.utils.html import strip_tags
from django.template.defaultfilters import truncatewords

from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route


from common.utils import DEFAULT_PAGE_KEY, paginate

from blog.feeds import BlogIndexPageFeed
from blog.utils import BlogFilter
from statistics.blocks import StatisticsBlock
from common.models import PersonPage, OrganizationPage, MetadataPageMixin
from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
    StyledTextBlock,
    AlignedCaptionedImageBlock,
    AlignedCaptionedEmbedBlock,
    RichTextBlockQuoteBlock,
)


class BlogIndexPage(RoutablePageMixin, MetadataPageMixin, Page):
    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
    ])

    about_blog_title = models.CharField(max_length=255, blank=True, null=True)
    feed_limit = models.PositiveIntegerField(
        default=20,
        help_text='Maximum number of posts to be included in the '
                  'syndication feed. 0 for unlimited.'
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('about_blog_title'),
        FieldPanel('feed_limit'),
    ]

    subpage_types = ['blog.BlogPage']

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    @route(r'^feed/$')
    def feed(self, request):
        return BlogIndexPageFeed(self)(request)

    def get_posts(self):
        return BlogPage.objects.child_of(self)\
                       .live()\
                       .order_by('-publication_datetime')

    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)

        post_filters = BlogFilter.from_querystring(request.GET)
        entry_qs = post_filters.filter(self.get_posts())

        if post_filters.author:
            context['author_filter'] = PersonPage.objects.get(pk=post_filters.author)
        if post_filters.organization:
            context['organization_filter'] = OrganizationPage.objects.get(pk=post_filters.organization)

        paginator, entries = paginate(
            request,
            entry_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=8,
            orphans=5
        )

        context['entries_page'] = entries
        context['paginator'] = paginator

        if request.is_ajax():
            context['layout_template'] = 'base.ajax.html'
        else:
            context['layout_template'] = 'base.html'

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


class BlogPage(MetadataPageMixin, Page):
    publication_datetime = models.DateTimeField(
        help_text='Past or future date of publication'
    )

    body = StreamField([
        ('text', StyledTextBlock(label='Text', template='common/blocks/styled_text_full_bleed.html')),
        ('image', AlignedCaptionedImageBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('blockquote', RichTextBlockQuoteBlock()),
        ('list', blocks.ListBlock(
            blocks.CharBlock(label="List Item"),
            template='common/blocks/list_block_columns.html'
        )),
        ('video', AlignedCaptionedEmbedBlock()),
        ('heading_1', Heading1()),
        ('heading_2', Heading2()),
        ('heading_3', Heading3()),
        ('statistics', StatisticsBlock()),
    ])

    link_to_original_post = models.URLField(blank=True, null=True)

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
        help_text='Image description displayed below the image. Organization/Photographer can be set via the image attribution.'
    )

    teaser_text = RichTextField(
        null=True,
        blank=True
    )

    organization = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
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
        StreamFieldPanel('body'),
        FieldPanel('link_to_original_post'),
        MultiFieldPanel(
            heading='Teaser',
            children=[
                ImageChooserPanel('teaser_image'),
                FieldPanel('image_caption'),
                FieldPanel('teaser_text'),
            ]
        ),
        PageChooserPanel('organization', 'common.OrganizationPage'),
        PageChooserPanel('author', 'common.PersonPage'),
    ]

    parent_page_types = ['blog.BlogIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('body', partial=True),
        index.SearchField('teaser_text'),
        index.FilterField('publication_datetime'),
    ]

    def get_meta_image(self):
        return self.teaser_image or super(BlogPage, self).get_meta_image()

    def get_meta_description(self):
        if self.teaser_text:
            return strip_tags(self.teaser_text)

        if self.search_description:
            return self.search_description

        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )
