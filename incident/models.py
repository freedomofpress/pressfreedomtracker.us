from django.db import models
from django.forms import CheckboxSelectMultiple, ChoiceField

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, StreamFieldPanel,
    InlinePanel, PageChooserPanel, MultiFieldPanel,
)
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsearch import index
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase

from . import choices


class IncidentIndexPage(Page):
    content_panels = Page.content_panels

    subpage_types = ['incident.IncidentPage']


class IncidentPage(Page):
    date = models.DateTimeField()
    affiliation = models.CharField(
        max_length=255,
        default='Independent',
        blank=True,
        null=True,
    )
    location = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )

    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
    ])

    teaser_image = models.ForeignKey(
        'wagtailimages.image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    targets = ParentalManyToManyField(
        'wagtailcore.Page',
        blank=True,
        related_name='targets',
        verbose_name='Targets (Journalists/Organizations)',
    )

    tags = ClusterTaggableManager(through='common.Tag', blank=True)

    related_incidents = ParentalManyToManyField('self', blank=True)

    # Detention/Arrest
    status_of_charges = models.CharField(
        choices=choices.STATUS_OF_CHARGES,
        max_length=255,
        null=True,
        blank=True,
    )
    is_in_custody = models.BooleanField(default=False)
    unnecessary_use_of_force = models.BooleanField(default=False)
    charges = ClusterTaggableManager(
        through='incident.ChargesTag',
        blank=True,
        related_name='charge_incidents',
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        ImageChooserPanel('teaser_image'),

        FieldPanel('date'),
        FieldPanel('affiliation'),
        FieldPanel('location'),
        # This will require some future filtering.
        FieldPanel('targets', widget=CheckboxSelectMultiple),
        FieldPanel('tags'),

        MultiFieldPanel(
            heading='Detention/Arrest',
            children=[
                FieldPanel('status_of_charges'),
                FieldPanel('is_in_custody'),
                FieldPanel('unnecessary_use_of_force'),
                FieldPanel('charges'),
            ]
        ),

        InlinePanel('categories', label='Incident categories', min_num=1),
        InlinePanel('updates', label='Updates'),

        FieldPanel('related_incidents')
    ]

    parent_page_types = ['incident.IncidentIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('body'),
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


class IncidentCategorization(Orderable):
    incident_page = ParentalKey(IncidentPage, related_name='categories')
    category = ParentalKey('common.CategoryPage', related_name='incidents')


class ChargesTag(TaggedItemBase):
    content_object = ParentalKey(
        'incident.IncidentPage',
        related_name='tagged_charges',
    )
