from inspect import signature
from django import forms
from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel, PageChooserPanel
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField

from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsearch import index
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
    LogoListBlock,
    StyledTextBlock,
    AlignedCaptionedImageBlock,
    AlignedCaptionedEmbedBlock,
    RichTextBlockQuoteBlock,
)
from common.choices import CATEGORY_COLOR_CHOICES
from common.utils import DEFAULT_PAGE_KEY, paginate
from statistics.registry import get_numbers_choices, get_numbers


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
    website = models.URLField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel('bio'),
        FieldPanel('website'),
        ImageChooserPanel('photo'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('bio'),
    ]


class QuickFact(Orderable):
    page = ParentalKey('common.CategoryPage', related_name='quick_facts')
    body = RichTextField()
    link_url = models.URLField(null=True, blank=True)


class NumbersIterable(object):
    def __iter__(self):
        return get_numbers_choices().__iter__()


number_list = NumbersIterable()
number_select = forms.Select()
number_select.choices = number_list


class DataItem(Orderable):
    page = ParentalKey('common.CategoryPage', related_name='data_items')
    label = models.CharField(max_length=255)
    data_point = models.CharField(max_length=255)
    params = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Whitespace-separated list of arguments to be passed to the data point function',
    )
    panels = [
        FieldPanel('label'),
        FieldPanel('data_point', widget=number_select),
        FieldPanel('params'),
    ]


class TaxonomyCategoryPage(Orderable):
    taxonomy_setting = ParentalKey('common.TaxonomySettings', related_name='categories')
    category = ParentalKey('common.CategoryPage', related_name='taxonomy_settings')

    panels = [
        PageChooserPanel('category', 'common.CategoryPage'),
    ]


class CategoryPage(Page):
    methodology = RichTextField(null=True, blank=True)
    plural_name = models.CharField(max_length=255, null=True, blank=True)
    page_color = models.CharField(max_length=255, choices=CATEGORY_COLOR_CHOICES, default='eastern-blue')

    content_panels = Page.content_panels + [
        FieldPanel('methodology'),
        InlinePanel('quick_facts', label='Quick Facts'),
        InlinePanel('data_items', label='Data Items'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('plural_name'),
        FieldPanel('page_color'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('methodology'),
    ]

    def get_context(self, request):
        # placed here to avoid circular dependency
        from incident.utils.incident_filter import IncidentFilter
        from incident.models.choices import get_filter_choices
        from home.models import HomePage

        context = super(CategoryPage, self).get_context(request)

        incident_filter = IncidentFilter.from_request(request)
        incident_filter.categories = str(self.page_ptr_id)
        context['category_options'] = incident_filter.get_category_options()
        context['export_path'] = HomePage.objects.live()[0].incident_index_page.url
        context['filter_choices'] = get_filter_choices()
        summary, entry_qs = incident_filter.fetch()

        paginator, entries = paginate(
            request,
            entry_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=8,
            orphans=5
        )

        context['entries_page'] = entries
        context['paginator'] = paginator
        context['summary_table'] = summary

        if request.is_ajax():
            context['layout_template'] = 'base.ajax.html'
        else:
            context['layout_template'] = 'base.html'

        def evaluate_statistic(name, params):
            fn = get_numbers()[name]
            param_count = len(signature(fn).parameters)
            if params:
                args = params.split()[:param_count]
                return fn(*args)
            elif param_count == 0:
                return fn()
            else:
                # This means number of parameters given does not match
                # the number expected by the function.
                return ''

        # Check for the presence of non-'page' querystring values
        filters = dict(request.GET)
        try:
            filters.pop('page')
        except KeyError:
            pass
        context['filtered'] = bool(filters)

        context['data_items'] = [
            {
                'label': item.label,
                'value': evaluate_statistic(item.data_point, item.params),
            } for item in self.data_items.all()
        ]
        return context


class SimplePage(Page):
    body = StreamField([
        ('text', StyledTextBlock(label='Text', template='common/blocks/styled_text_full_bleed.html')),
        ('image', AlignedCaptionedImageBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('blockquote', RichTextBlockQuoteBlock()),
        ('list', blocks.ListBlock(
            blocks.CharBlock(label="List Item"),
            template='common/blocks/list_block_columns.html'
        )),
        ('logo_list', LogoListBlock()),
        ('video', AlignedCaptionedEmbedBlock()),
        ('heading_1', Heading1()),
        ('heading_2', Heading2()),
        ('heading_3', Heading3()),
    ])

    sidebar_content = StreamField([
        ('heading', Heading2()),
        ('rich_text', blocks.RichTextBlock()),
    ], default=None)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        StreamFieldPanel('sidebar_content')
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    def get_context(self, request):
        # Avoid circular import
        from home.models import HomePage

        context = super(SimplePage, self).get_context(request)

        home = Page.objects.all().live().type(
            HomePage)[0]

        context['home_page'] = home

        return context


class SimplePageWithSidebar(BaseSidebarPageMixin, Page):
    body = StreamField([
        ('text', StyledTextBlock(label='Text')),
        ('image', AlignedCaptionedImageBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('blockquote', RichTextBlockQuoteBlock()),
        ('list', blocks.ListBlock(
            blocks.CharBlock(label="List Item"),
            template='common/blocks/list_block_columns.html'
        )),
        ('logo_list', LogoListBlock()),
        ('video', AlignedCaptionedEmbedBlock()),
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
