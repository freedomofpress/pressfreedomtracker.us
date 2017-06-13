from __future__ import absolute_import, unicode_literals
from django.db import models

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    PageChooserPanel,
    MultiFieldPanel,
)
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, Orderable

from modelcluster.fields import ParentalKey


class HomePage(Page):
    about = RichTextField(
        blank=True,
        null=True,
        help_text='Headings and line breaks will be stripped'
    )

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

    incident_index_page = models.ForeignKey(
        'incident.IncidentIndexPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    statboxes_label = models.CharField(
        blank=True,
        null=True,
        default='Quick Stats',
        max_length=255,
        help_text='Title displayed above stat boxes'
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('statboxes_label'),
            InlinePanel(
                'statboxes',
                label='Statboxes',
            ),
        ], 'Statboxes'),
        FieldPanel('about'),
        PageChooserPanel(
            'about_page',
            [
                'common.SimplePage',
                'common.SimplePageWithSidebar'
            ]
        ),
        PageChooserPanel('blog_index_page', 'blog.BlogIndexPage'),
        PageChooserPanel('incident_index_page', 'incident.IncidentIndexPage'),
        InlinePanel(
            'incidents',
            label='Featured Incidents',
            min_num=4,
            max_num=6,
        ),
    ]


class HomePageIncidents(Orderable):
    page = ParentalKey('home.HomePage', related_name='incidents')
    incident = models.ForeignKey(
        'incident.IncidentPage',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    panels = [
        PageChooserPanel('incident', 'incident.IncidentPage'),
    ]


class StatBox(Orderable):
    page = ParentalKey('home.HomePage', related_name='statboxes')
    value = models.CharField(max_length=1000)
    label = models.CharField(max_length=1000)
    color = models.CharField(
        max_length=7,
        choices=[
            ('#119abc', 'Blue'),
            ('#5b9932', 'Green'),
            ('#803e79', 'Purple'),
            ('#dc810b', 'Orange'),
            ('#2d2e2e', 'Dark Gray'),
        ],
    )
    link = models.ForeignKey(
        'wagtailcore.Page',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    panels = [
        FieldPanel('value'),
        FieldPanel('label'),
        FieldPanel('color'),
        PageChooserPanel('link')
    ]
