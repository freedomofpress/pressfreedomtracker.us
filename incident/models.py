from django.db import models

from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailsearch import index
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField

from common.utils import DEFAULT_PAGE_KEY, paginate


class IncidentIndexPage(Page):
    content_panels = Page.content_panels

    subpage_types = ['incident.IncidentPage']

    def get_incidents(self):
        """Returns all published incident pages"""
        return IncidentPage.objects.live()

    def get_context(self, request):
        context = super(IncidentIndexPage, self).get_context(request)

        entry_qs = self.get_incidents()

        paginator, entries = paginate(request, entry_qs,
                                      page_key=DEFAULT_PAGE_KEY,
                                      per_page=8,
                                      orphans=5)

        context['entries_page'] = entries
        context['paginator'] = paginator

        return context


class IncidentPage(Page):
    date = models.DateTimeField()

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

    journalists = ParentalManyToManyField('common.PersonPage', blank=True)

    tags = ClusterTaggableManager(through='common.Tag', blank=True)

    related_incidents = ParentalManyToManyField('self', blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        StreamFieldPanel('body'),
        FieldPanel('journalists'),
        FieldPanel('tags'),
        InlinePanel('categories', label='Incident categories', min_num=1),
        InlinePanel('updates', label='Updates'),
        ImageChooserPanel('teaser_image'),
        FieldPanel('related_incidents')
    ]

    parent_page_types = ['incident.IncidentIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    def last_updated(self):
        """
        Returns the date this incident was last updated on.
        """
        first = self.updates.first()
        if first:
            return first.date
        return self.first_published_at

    def get_main_category(self):
        """
        Returns the first category in the list of categories
        """
        return self.categories.all().first().category

    def get_related_incidents(self):
        """
        Returns related incidents or other incidents in the same category
        """
        if self.related_incidents.all():
            return self.related_incidents.all()
        else:
            main_category = self.get_main_category()

            related_incidents = IncidentPage.objects.filter(
                live=True,
                categories__category=main_category
            ).exclude(id=self.id)

            # Only return two related incidents (Categories have too many incidents)
            return related_incidents[:2]


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
