from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, PageChooserPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page
from modelcluster.contrib.taggit import ClusterTaggableManager

from wagtail.wagtailimages.blocks import ImageChooserBlock


class IncidentPage(Page):
    date = models.DateTimeField()

    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
    ])

    category = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='incidents'
    )

    tags = ClusterTaggableManager(through='common.Tag', blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        StreamFieldPanel('body'),
        PageChooserPanel('category', 'common.CategoryPage'),
        FieldPanel('tags')
    ]
