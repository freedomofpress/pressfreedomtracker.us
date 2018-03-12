from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Orderable
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel

from incident.utils.incident_filter import IncidentFilter


@register_setting(icon='search')
class SearchSettings(BaseSetting):
    search_page = models.ForeignKey(
        'incident.IncidentIndexPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Incident index page to use for search and for "Recent incidents" feeds',
        verbose_name='Incident search page',
    )

    panels = [
        PageChooserPanel('search_page'),
    ]

    class Meta:
        verbose_name = 'Incident search'


@register_setting
class FooterSettings(BaseSetting):
    body = RichTextField(blank=True, null=True)
    menu = models.ForeignKey(
        'menus.Menu',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    partner_logo_text = models.CharField(max_length=255, blank=True, null=True)
    partner_logo_link = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    panels = [
        FieldPanel('body'),
        SnippetChooserPanel('menu'),
        FieldPanel('partner_logo_text'),
        PageChooserPanel('partner_logo_link')
    ]

    class Meta:
        verbose_name = 'Site Footer'


@register_setting
class TaxonomySettings(BaseSetting, ClusterableModel):
    panels = [
        InlinePanel(
            'categories',
            label='Incident Categories',
            help_text='The categories listed here will be used for navigation menus throughout the site.',
        ),
    ]

    class Meta:
        verbose_name = 'Taxonomy'


@register_setting(icon='plus')
class SocialSharingSEOSettings(BaseSetting):
    default_description = models.TextField(
        blank=True,
        null=True,
        help_text='Default text description for pages that don\'t have another '
                  'logical field for text descirptions'
    )

    default_image = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Default image for pages that don\'t have another '
                  'logical image for social sharing'
    )

    facebook_page_id = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text='Find on your Facebook page by navigating to "About" and '
                  'scrolling to the bottom'
    )

    twitter = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        help_text='Your Twitter username'
    )

    panels = [
        FieldPanel('default_description'),
        ImageChooserPanel('default_image'),
        FieldPanel('facebook_page_id'),
        FieldPanel('twitter'),
    ]

    class Meta:
        verbose_name = 'Social Sharing/SEO'


@register_setting
class IncidentFilterSettings(BaseSetting, ClusterableModel):
    class Meta:
        verbose_name = 'Incident Filters'

    panels = [
        InlinePanel(
            'general_incident_filters',
            label='Fields to include in filters',
            min_num=1,
        ),
    ]


class GeneralIncidentFilter(Orderable):
    incident_filter_settings = ParentalKey(IncidentFilterSettings, related_name='general_incident_filters')
    incident_filter = models.CharField(max_length=255, choices=IncidentFilter.get_filter_choices())
