from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
)
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable
from wagtail.images.blocks import ImageChooserBlock

from common.blocks import (
    AlignedCaptionedEmbedBlock,
    RichTextBlockQuoteBlock,
    RichTextTemplateBlock,
)
from wagtailautocomplete.edit_handlers import AutocompletePanel
from statistics.blocks import StatisticsBlock


class IncidentPageUpdates(Orderable):
    page = ParentalKey('incident.IncidentPage', related_name='updates')
    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    body = StreamField([
        ('rich_text', RichTextTemplateBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('blockquote', RichTextBlockQuoteBlock()),
        ('video', AlignedCaptionedEmbedBlock()),
        ('statistics', StatisticsBlock()),
    ])

    panels = [
        FieldPanel('title'),
        FieldPanel('date'),
        StreamFieldPanel('body'),
    ]

    def __str__(self):
        return '({}) {}'.format(self.date, self.title)


class IncidentCategorization(Orderable):
    incident_page = ParentalKey('incident.IncidentPage', related_name='categories')
    category = ParentalKey('common.CategoryPage', related_name='incidents')

    @property
    def summary(self):
        return self.category.title


class IncidentPageLinks(Orderable):
    page = ParentalKey('incident.IncidentPage', related_name='links')
    title = models.CharField(max_length=255, null=False, blank=False)
    url = models.URLField(max_length=1024, blank=False)
    publication = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        value = '{} ({})'.format(self.title, self.url)
        if self.publication:
            value += ' via {}'.format(self.publication)
        return value


class EquipmentSeized(models.Model):
    incident = ParentalKey(
        'incident.IncidentPage',
        related_name='equipment_seized',
    )
    equipment = ParentalKey(
        'incident.Equipment',
        verbose_name='Equipment Seized',
    )
    quantity = models.PositiveSmallIntegerField(default=1)
    _autocomplete_model = 'incident.Equipment'

    panels = [
        AutocompletePanel('equipment', page_type='incident.Equipment'),
        FieldPanel('quantity'),
    ]

    class Meta:
        verbose_name = "Equipment Seized"

    @property
    def summary(self):
        return '{0.equipment}: count of {0.quantity}'.format(self)


class EquipmentBroken(models.Model):
    incident = ParentalKey(
        'incident.IncidentPage',
        related_name='equipment_broken',
    )
    equipment = ParentalKey(
        'incident.Equipment',
        verbose_name='Equipment Broken',
    )
    quantity = models.PositiveSmallIntegerField(default=1)
    _autocomplete_model = 'incident.Equipment'

    panels = [
        AutocompletePanel('equipment', page_type='incident.Equipment'),
        FieldPanel('quantity'),
    ]

    class Meta:
        verbose_name = 'Equipment Broken'

    @property
    def summary(self):
        return '{0.equipment}: count of {0.quantity}'.format(self)
