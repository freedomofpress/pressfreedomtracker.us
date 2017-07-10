from django.db import models
from django.utils.cache import patch_cache_control

from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsearch import index

from common.utils import DEFAULT_PAGE_KEY, paginate

from statistics.blocks import StatisticsBlock


class BlogIndexPage(Page):
    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    subpage_types = ['blog.BlogPage']

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    def get_context(self, request):
        context = super(BlogIndexPage, self).get_context(request)

        entry_qs = self.get_children().live()

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

    # The following method is in large part copied from incident_index_page.py.
    def serve(self, request, *args, **kwargs):
        response = super(BlogIndexPage, self).serve(request, *args, **kwargs)
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


class BlogPage(Page):
    publication_datetime = models.DateTimeField(
        help_text='Past or future date of publication'
    )

    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('statistics', StatisticsBlock()),
    ])

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
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content_panels = Page.content_panels + [
        FieldPanel('publication_datetime'),
        StreamFieldPanel('body'),
        FieldPanel('teaser_text'),
        PageChooserPanel('organization', 'common.OrganizationPage'),
        PageChooserPanel('author', 'common.PersonPage'),
    ]

    parent_page_types = ['blog.BlogIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('body', partial=True),
        index.SearchField('teaser_text'),
        index.FilterField('publication_datetime'),
    ]
