from django.core.validators import MaxValueValidator
from django.db import models

from wagtail.contrib.settings.models import BaseSetting
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page, Orderable

from wagtail.wagtailimages.blocks import ImageChooserBlock

class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
    ]

class BlogPage(BaseSetting):
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

  content_panels = Page.content_panels + [
    FieldPanel('publication_datetime'),
    FieldPanel('body'),
    FieldPanel('teaser_text')
  ]

