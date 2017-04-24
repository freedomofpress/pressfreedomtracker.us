from __future__ import absolute_import, unicode_literals
from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.blocks import ImageChooserBlock
from modelcluster.fields import ParentalKey


class HomePage(Page):
    about = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
    ], null=True)

    incident_index_page = ParentalKey('incident.IncidentIndexPage', related_name='homepage',
                                      null=True, blank=True, on_delete=models.SET_NULL)


    content_panels = Page.content_panels + [
        StreamFieldPanel('about'),
        FieldPanel('incident_index_page')
    ]

