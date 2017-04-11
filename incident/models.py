from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel, InlinePanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.blocks import ImageChooserBlock

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager


class IncidentPage(Page):
    date = models.DateTimeField()

    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
    ])

    tags = ClusterTaggableManager(through='common.Tag', blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        StreamFieldPanel('body'),
        FieldPanel('tags'),
        InlinePanel('related_incidents', label='Related incidents'),
        InlinePanel('updates', label='Updates')
    ]

    parent_page_types = ['common.CategoryPage']


class IncidentPageRelatedLinks(Orderable):
    page = ParentalKey(IncidentPage, related_name='related_incidents')
    related_incident = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='incidents'
    )

    panels = [
        PageChooserPanel('related_incident', IncidentPage)
    ]


class IncidentPageUpdates(Orderable):
    page = ParentalKey(IncidentPage, related_name='updates')
    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
    ])

    panels = [
        FieldPanel('title'),
        FieldPanel('date'),
        StreamFieldPanel('body'),
    ]
