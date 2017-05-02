from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch import index

from wagtail.wagtailimages.blocks import ImageChooserBlock


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


class BlogPage(Page):
    publication_datetime = models.DateTimeField(
        help_text='Past or future date of publication'
    )

    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
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
        index.SearchField('body'),
        index.SearchField('teaser_text'),
        index.FilterField('publication_datetime'),
    ]
