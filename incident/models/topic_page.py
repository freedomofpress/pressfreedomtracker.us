from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailautocomplete.edit_handlers import AutocompletePanel

import common.blocks
from common.models import MetadataPageMixin
from common.utils import (
    DEFAULT_PAGE_KEY,
    paginate,
)
from incident.models import IncidentPage


class TopicPage(MetadataPageMixin, Page):
    TOP_LEFT = 'top-left'
    BOTTOM_LEFT = 'bottom-left'
    TOP_CENTER = 'top-center'
    BOTTOM_CENTER = 'bottom-center'

    TEXT_ALIGN_CHOICES = (
        (TOP_CENTER, 'Top Center'),
        (BOTTOM_CENTER, 'Bottom Center'),
        (TOP_LEFT, 'Top Left'),
        (BOTTOM_LEFT, 'Bottom Left'),
    )

    WHITE = 'white'
    BLACK = 'black'
    TEXT_COLOR_CHOICES = (
        (WHITE, 'White'),
        (BLACK, 'Black'),
    )

    superheading = models.TextField(
        help_text='Text that appears above the title in the heading block',
        blank=True,
        null=True
    )
    description = RichTextField(
        features=['bold', 'italic', 'links'],
        blank=True
    )
    text_align = models.CharField(
        max_length=255, choices=TEXT_ALIGN_CHOICES, default=BOTTOM_CENTER,
        help_text='Alignment of the full header text within the header image'
    )
    text_color = models.CharField(
        max_length=255, choices=TEXT_COLOR_CHOICES, default=WHITE,
        help_text='Color of header text, for legibility against the background.'
    )
    photo_caption = RichTextField(
        features=['bold', 'italic', 'links'],
        blank=True
    )
    photo_credit = models.TextField(blank=True)
    photo_credit_link = models.URLField(blank=True, null=True)
    photo = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content = StreamField([
        ('heading_2', common.blocks.Heading2()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('rich_text', blocks.RichTextBlock()),
    ], blank=True)
    sidebar = StreamField([
        ('heading_2', common.blocks.Heading2()),
        ('rich_text', common.blocks.RichTextTemplateBlock(
            features=['bold', 'italic', 'link', 'ol', 'ul'],
            icon='doc-full',
            label='Rich Text',
        )),
        ('stat_table', common.blocks.StatTableBlock()),
        ('button', common.blocks.ButtonBlock()),
    ], blank=True)
    incident_tag = models.ForeignKey('common.CommonTag', on_delete=models.PROTECT)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            heading='Header',
            children=[
                FieldPanel('superheading'),
                FieldPanel('description'),
                FieldPanel('text_align'),
                FieldPanel('text_color'),
                ImageChooserPanel('photo'),
                FieldPanel('photo_caption'),
                FieldPanel('photo_credit'),
                FieldPanel('photo_credit_link'),
            ],
            classname='collapsible'
        ),
        MultiFieldPanel(
            heading='Content',
            children=[
                StreamFieldPanel('content'),
                StreamFieldPanel('sidebar'),
            ],
            classname='collapsible',
        ),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            heading='Incidents',
            children=[
                AutocompletePanel('incident_tag', page_type='common.CommonTag'),
            ],
            classname='collapsible',
        ),
    ]

    def get_context(self, request):
        context = super(TopicPage, self).get_context(request)

        incident_qs = IncidentPage.objects.live().filter(
            tags=self.incident_tag
        )

        paginator, entries = paginate(
            request,
            incident_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=8,
            orphans=5
        )

        context['entries_page'] = entries
        context['paginator'] = paginator

        return context
