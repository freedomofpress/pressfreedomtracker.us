from __future__ import absolute_import, unicode_literals
from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, Orderable

from modelcluster.fields import ParentalKey


class HomePage(Page):
    about = RichTextField(blank=True, null=True)

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

    content_panels = Page.content_panels + [
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
        InlinePanel('categories', label='Incident Categories'),
        InlinePanel(
            'incidents',
            label='Featured Incidents',
            min_num=4,
            max_num=6,
        )
    ]

    def get_context(self, *args):
        context = super(HomePage, self).get_context(*args)
        context['recent_incidents'] = [
            dict(number=49, label="Trump tweets insulting reporters", color="#119abc"),
            dict(number=6, label="journalist equipment seizures", color="#5b9932"),
            dict(number=2, label="journalist border stops", color="#803e79"),
            dict(number=12, label="journalist arrests", color="#dc810b"),
        ]
        return context


class HomePageCategories(Orderable):
    page = ParentalKey('home.HomePage', related_name='categories')
    category = models.ForeignKey(
        'common.CategoryPage',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    panels = [
        PageChooserPanel('category', 'common.CategoryPage'),
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
