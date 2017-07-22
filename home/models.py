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

from common.choices import CATEGORY_COLOR_CHOICES
from incident.models.choices import get_filter_choices
from incident.utils.incident_filter import IncidentFilter


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
        related_name='+',
        help_text='Recent blog posts will automatically be pulled from this page'
    )

    incident_index_page = models.ForeignKey(
        'incident.IncidentIndexPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Recent incidents will automatically be pulled from this page'
    )

    statboxes_label = models.CharField(
        default='Quick Stats',
        max_length=255,
        help_text='Title displayed above stat boxes'
    )

    featured_incidents_label = models.CharField(
        default='Featured Incidents',
        max_length=255,
        help_text='Title displayed above featured incidents'
    )

    featured_more_label = models.CharField(
        default='More Incidents',
        max_length=255,
        help_text='Text for button to show more incidents'
    )

    recent_incidents_label = models.CharField(
        default='Recent Incidents',
        max_length=255,
        help_text='Title displayed above recent incidents'
    )

    recent_more_label = models.CharField(
        default='More Incidents',
        max_length=255,
        help_text='Text for button to show more incidents'
    )

    blog_label = models.CharField(
        default='Partner Articles',
        max_length=255,
        help_text='Title displayed above blog posts'
    )

    blog_more_label = models.CharField(
        default='More Articles',
        max_length=255,
        help_text='Text for button to show more blog posts'
    )

    change_filters_message = models.CharField(
        default='Change filters to search the incident database.',
        max_length=255,
        help_text='Text for the filter bar when no filters are applied.',
    )

    content_panels = Page.content_panels + [

        MultiFieldPanel([
            FieldPanel('statboxes_label'),
            InlinePanel(
                'statboxes',
                label='Statboxes',
            ),
        ], 'Statboxes'),

        MultiFieldPanel([
            FieldPanel('featured_incidents_label'),
            InlinePanel(
                'incidents',
                label='Featured Incidents',
                min_num=4,
                max_num=6,
            ),
        ], 'Featured Incidents'),

        MultiFieldPanel([
            FieldPanel('about'),
            PageChooserPanel(
                'about_page',
                [
                    'common.SimplePage',
                    'common.SimplePageWithSidebar'
                ]
            ),
        ], 'About'),

        MultiFieldPanel([
            FieldPanel('recent_incidents_label'),
            PageChooserPanel('incident_index_page', 'incident.IncidentIndexPage'),
        ], 'Recent Incidents'),

        MultiFieldPanel([
            FieldPanel('blog_label'),
            PageChooserPanel('blog_index_page', 'blog.BlogIndexPage'),
        ], 'Blog'),

        MultiFieldPanel([
            FieldPanel('change_filters_message'),
        ], 'Filter Bar'),

    ]

    def get_context(self, request):
        context = super(HomePage, self).get_context(request)

        incident_filter = IncidentFilter.from_request(request)
        context['category_options'] = incident_filter.get_category_options()
        context['export_path'] = self.incident_index_page.url
        context['filter_choices'] = get_filter_choices()

        return context


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
        max_length=255,
        choices=CATEGORY_COLOR_CHOICES,
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
