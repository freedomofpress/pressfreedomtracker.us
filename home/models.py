from __future__ import absolute_import, unicode_literals

import json

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    PageChooserPanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page, Orderable, Site

import common.blocks
from common.choices import CATEGORY_COLOR_CHOICES
from common.models import MetadataPageMixin
from common.models.settings import SearchSettings
from common.utils import unescape
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

    featured_pages_label = models.CharField(
        default='Featured Articles',
        max_length=255,
        help_text='Title displayed above featured pages'
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

    content = StreamField([
        ('heading_2', common.blocks.Heading2()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('rich_text', blocks.RichTextBlock()),
        ('tweet', common.blocks.TweetEmbedBlock()),
        ('tabs', common.blocks.TabbedBlock()),
    ], blank=True)

    content_panels = Page.content_panels + [

        MultiFieldPanel(
            [
                FieldPanel('statboxes_label'),
                InlinePanel(
                    'statboxes',
                    label='Statboxes',
                ),
            ],
            'Statboxes',
            classname='collapsible',
        ),
        StreamFieldPanel('content'),
        MultiFieldPanel([
            FieldPanel('featured_pages_label'),
            InlinePanel(
                'features',
                label='Featured Pages',
                min_num=4,
                max_num=6,
            ),
        ], 'Featured Pages'),

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

    def get_context(self, request, *args, **kwargs):
        context = super(HomePage, self).get_context(request, *args, **kwargs)

        context['serialized_filters'] = json.dumps(get_serialized_filters())

        search_settings = SearchSettings.for_site(Site.find_for_request(request))

        if search_settings.data_download_page:
            context['export_path'] = search_settings.data_download_page.get_url()
        elif search_settings.search_page:
            context['export_path'] = search_settings.search_page.get_url() + search_settings.search_page.reverse_subpage('export_view')
        else:
            context['export_path'] = None

        context['features'] = [
            f.page.specific for f in self.features.all().select_related('page__content_type')
        ]
        return context


class HomePageFeature(Orderable):
    home_page = ParentalKey('home.HomePage', related_name='features')
    page = models.ForeignKey(Page, on_delete=models.CASCADE)

    panels = [
        PageChooserPanel('page', ('blog.BlogPage', 'incident.IncidentPage', 'incident.TopicPage')),
    ]


class StatBox(Orderable):
    page = ParentalKey(Page, related_name='statboxes')
    value = RichTextField(
        blank=True,
        null=True,
        help_text='Primary text for this stat box.  Line breaks will be removed.',
        validators=[validate_template],
        features=['bold', 'italic', 'numincidents'],
    )
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

    def clean(self):
        self.value = unescape(self.value)
