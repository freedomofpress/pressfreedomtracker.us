from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel, PageChooserPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsearch import index
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
)


class BaseSidebarPageMixin(models.Model):
    """
    A mixin that gives a model a sidebar menu field and the ability to
    intelligently use its own sidebar menu or a parent's sidebar menu.
    """

    sidebar_menu = models.ForeignKey(
        'menus.Menu',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='If left empty, page will use parent\'s sidebar menu'
    )

    settings_panels = [
        SnippetChooserPanel('sidebar_menu'),
    ]

    def get_sidebar_menu(self):
        """
        Return own sidebar menu if it exists. Otherwise, return the nearest
        ancestor's sidebar menu.
        """

        if self.sidebar_menu:
            return self.sidebar_menu

        try:
            return self.get_parent().specific.get_sidebar_menu()
        except AttributeError:
            return None

    class Meta:
        abstract = True


class OrganizationIndexPage(Page):
    subpage_types = ['common.OrganizationPage']
    content_panels = Page.content_panels

    subpage_types = ['common.OrganizationPage']


class OrganizationPage(Page):
    website = models.URLField(blank=True, null=True)
    logo = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    description = RichTextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('website'),
        ImageChooserPanel('logo'),
    ]

    parent_page_types = ['common.OrganizationIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('website', partial_match=True),
        index.SearchField('description'),
    ]


class PersonPage(Page):
    photo = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    bio = RichTextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('bio'),
        ImageChooserPanel('photo'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('bio'),
    ]


class QuickFact(Orderable):
    page = ParentalKey('common.CategoryPage', related_name='quick_facts')
    body = RichTextField()
    link_url = models.URLField(null=True, blank=True)


class TaxonomyCategoryPage(Orderable):
    taxonomy_setting = ParentalKey('common.TaxonomySettings', related_name='categories')
    category = ParentalKey('common.CategoryPage', related_name='taxonomy_settings')

    panels = [
        PageChooserPanel('category', 'common.CategoryPage'),
    ]


class CategoryPage(Page):
    description = RichTextField(null=True, blank=True)
    methodology = RichTextField(null=True, blank=True)
    plural_name = models.CharField(max_length=255, null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        FieldPanel('methodology'),
        InlinePanel('quick_facts', label='Quick Facts')
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('plural_name'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('description'),
        index.SearchField('methodology'),
    ]

    def get_context(self, request):
        # placed here to avoid circular dependency
        from incident.utils import IncidentFilter

        context = super(CategoryPage, self).get_context(request)
        context['incidents'] = IncidentFilter(
            search_text=request.GET.get('search'),
            lower_date=request.GET.get('lower_date'),
            upper_date=request.GET.get('upper_date'),
            categories=str(self.page_ptr_id),
        ).fetch()
        return context


class SimplePage(Page):
    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('heading_1', Heading1()),
        ('heading_2', Heading2()),
        ('heading_3', Heading3()),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]


class SimplePageWithSidebar(BaseSidebarPageMixin, Page):
    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('heading_1', Heading1()),
        ('heading_2', Heading2()),
        ('heading_3', Heading3()),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    settings_panels = Page.settings_panels + BaseSidebarPageMixin.settings_panels

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]


class CommonTag(ClusterableModel):
    @classmethod
    def autocomplete_create(kls, value):
        return kls.objects.create(title=value)

    title = models.CharField(
        max_length=255,
        unique=True,
    )

    def __str__(self):
        return self.title
