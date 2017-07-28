from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from modelcluster.models import ClusterableModel


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
