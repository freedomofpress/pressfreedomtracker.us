from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.core.blocks import RichTextBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from common.validators import validate_image_format, validate_template
from common.blocks import Heading2
from incident.utils.incident_filter import IncidentFilter


@register_setting(icon='search')
class SearchSettings(BaseSetting):
    data_download_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='+',
        help_text='Page linked to by the "Download the data" link at the bottom of the search filters. If a page is selected here, then the link will redirect to it with the search querystring intact. If this field is blank, the link will be a direct download of the CSV data requested.',
    )

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
        PageChooserPanel('data_download_page'),
    ]

    class Meta:
        verbose_name = 'Incident search'


@register_setting
class FooterSettings(BaseSetting, ClusterableModel):
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
        PageChooserPanel('partner_logo_link'),
        InlinePanel(
            'footer_logos',
            label="Footer Logos",
            min_num=3,
            max_num=6,
        ),
    ]

    class Meta:
        verbose_name = 'Site Footer'


class FooterLogos(Orderable):
    footer = ParentalKey(FooterSettings, related_name='footer_logos')
    logo_url = models.URLField(max_length=255, help_text='A URL or path for this logo to link to.')
    logo_image = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='+',
        help_text='A white logo with a transparent background, ideally PNG format',
        validators=[validate_image_format]
    )

    panels = [
        ImageChooserPanel('logo_image'),
        FieldPanel('logo_url'),
    ]


@register_setting
class SiteSettings(BaseSetting):
    incident_sidebar_note = StreamField(
        [
            ('heading', Heading2()),
            ('rich_text', RichTextBlock()),
        ],
        default=None,
        blank=True,
        null=True,
        help_text='Note that appears in the sidebar of incident pages, incident index pages, and category pages.'
    )
    banner_content = RichTextField(
        blank=True,
        null=True,
        help_text="If set an alert banner will appear on the site with this message",
        validators=[validate_template],
        features=['bold', 'italic', 'link'],
        verbose_name='Banner Content'
    )
    homepage_only = models.BooleanField(
        default=True,
        verbose_name='Homepage Only',
        help_text='Show banner <em>only</em> on homepage (if not set, will show sitewide)'
    )
    incident_footer = RichTextField(
        blank=True,
        null=True,
        default='<p>The <a href="https://pressfreedomtracker.us/">U.S. Press Freedom Tracker</a> catalogues press freedom violations in the United States. Email tips to tips@pressfreedomtracker.us.</p>',
        verbose_name='Incident Footer Call to Action'
    )

    panels = [
        StreamFieldPanel('incident_sidebar_note'),
        FieldPanel('incident_footer'),
        MultiFieldPanel([
            FieldPanel('banner_content'),
            FieldPanel('homepage_only')
        ], 'Alert Banner')
    ]

    class Meta:
        verbose_name = 'Site Settings'


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
        verbose_name = 'general incident filters'

    panels = [
        InlinePanel(
            'general_incident_filters',
            label='Filters',
            help_text='Selected filters will always be displayed, as part of the "General" filters section',
            min_num=1,
        ),
    ]


class GeneralIncidentFilter(Orderable):
    incident_filter_settings = ParentalKey(IncidentFilterSettings, related_name='general_incident_filters')
    incident_filter = models.CharField(max_length=255, choices=IncidentFilter.get_filter_choices(), unique=True)

    def clean(self):
        from common.models.pages import CategoryIncidentFilter
        try:
            category_incident_filter = CategoryIncidentFilter.objects.get(incident_filter=self.incident_filter)
        except CategoryIncidentFilter.DoesNotExist:
            pass
        else:
            raise ValidationError({
                'incident_filter': '"{}" is already in use by the "{}" category'.format(
                    self.get_incident_filter_display(),
                    category_incident_filter.category.title,
                ),
            })
