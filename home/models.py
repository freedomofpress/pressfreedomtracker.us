from __future__ import absolute_import, unicode_literals

import json

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    PageChooserPanel,
    MultiFieldPanel,
)
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page, Orderable

from common.choices import CATEGORY_COLOR_CHOICES
from common.models import MetadataPageMixin
from common.models.settings import SearchSettings
from common.validators import validate_template
from incident.utils.incident_filter import get_serialized_filters


class HomePage(MetadataPageMixin, Page):
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

        context['serialized_filters'] = json.dumps(get_serialized_filters())

        search_page = SearchSettings.for_site(request.site).search_page
        context['export_path'] = getattr(search_page, 'url', None)

        context['incidents'] = self.incidents.all().select_related('page')

        return context


class HomePageFeature(Orderable):
    home_page = ParentalKey('home.HomePage', related_name='incidents')
    page = models.ForeignKey(Page, on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('page', ('blog.BlogPage', 'incident.IncidentPage')),
    ]


class StatBox(Orderable):
    page = ParentalKey('home.HomePage', related_name='statboxes')
    value = models.CharField(max_length=1000, validators=[validate_template])
    label = models.CharField(max_length=1000)
    color = models.CharField(
        max_length=255,
        choices=CATEGORY_COLOR_CHOICES,
    )
    internal_link = models.ForeignKey(
        'wagtailcore.Page',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    querystring = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        help_text="Append a querystring to the internal link. Should start with '?'"
    )
    external_link = models.URLField(blank=True, help_text="This link will not be used if there is an internal link set.")

    panels = [
        FieldPanel('value'),
        FieldPanel('label'),
        FieldPanel('color'),
        PageChooserPanel('internal_link'),
        FieldPanel('querystring'),
        FieldPanel('external_link'),
    ]
