from __future__ import absolute_import, unicode_literals
from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
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

    about_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    blog_index_page = models.ForeignKey(
        'blog.BlogIndexPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    incident_index_page = ParentalKey('incident.IncidentIndexPage', related_name='homepage',
                                      null=True, blank=True, on_delete=models.SET_NULL)

    content_panels = Page.content_panels + [
        StreamFieldPanel('about'),
        FieldPanel('about_page'),
        FieldPanel('blog_index_page'),
        FieldPanel('incident_index_page'),
        InlinePanel('categories', label='Incident Categories')
    ]


class HomePageCategories(Orderable):
    page = ParentalKey('home.HomePage', related_name='categories')
    category = ParentalKey('common.CategoryPage', related_name='homepage')
