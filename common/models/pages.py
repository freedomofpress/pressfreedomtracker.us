import json

from django.core.exceptions import ValidationError
from django.db import models
from django.http import Http404
from django.shortcuts import redirect
from django.utils.html import strip_tags
from django.template.defaultfilters import truncatewords
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel, PageChooserPanel
from wagtail.core import blocks
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField

from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtailmetadata.models import MetadataPageMixin as OriginalMetadataPageMixin
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
    LogoListBlock,
    StyledTextBlock,
    StyledTextTemplateBlock,
    AlignedCaptionedImageBlock,
    AlignedCaptionedEmbedBlock,
    RichTextBlockQuoteBlock,
    EmailSignupBlock,
)
from common.choices import CATEGORY_COLOR_CHOICES
from common.utils import (
    DEFAULT_PAGE_KEY,
    paginate,
)
from common.templatetags.render_as_template import render_as_template
from common.validators import validate_template
from incident.utils.incident_filter import IncidentFilter
from statistics.registry import get_numbers_choices
from statistics.validators import validate_dataset_params
# Import statistics tags so that statistics dataset choices are populated
import statistics.templatetags.statistics_tags  # noqa: F401


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


class MetadataPageMixin(OriginalMetadataPageMixin):
    "Provide defaults for metadate for pages in this application"

    def _get_ssssettings(self):
        # Imported here to avoid circular dependency
        from common.models.settings import SocialSharingSEOSettings
        return SocialSharingSEOSettings.for_site(self.get_site())

    def get_meta_description(self):
        """
        Return either the search_description set on the page or the
        default description set for the site
        """

        if self.search_description:
            return self.search_description

        ssssettings = self._get_ssssettings()
        return ssssettings.default_description

    def get_meta_image(self):
        """
        Return either the search_image set on the page or the
        default image set for the site
        """

        if self.search_image:
            return self.search_image

        ssssettings = self._get_ssssettings()
        return ssssettings.default_image

    class Meta:
        abstract = True


class OrganizationIndexPage(Page):
    subpage_types = ['common.OrganizationPage']
    content_panels = Page.content_panels

    subpage_types = ['common.OrganizationPage']

    def serve(self, request):
        raise Http404()


class OrganizationPage(Page):
    website = models.URLField(blank=True)
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

    def serve(self, request):
        """
        Find a sample from this organization and deduce a URL for the
        BlogIndexPage for the BlogPage and filter by this organization.

        Note: this is not very robust. If this site ever grow to have multiple
        blog indexes, we will probably want to add a field to this page to
        explicitly specify which blog index to use
        """

        try:
            blog_index = self.blog_posts.all()[0].get_parent()
        except IndexError:
            # This organization has no blog posts. Fall back to 404
            raise Http404()
        return redirect('{}?organization={}'.format(blog_index.url, self.pk))


class PersonPage(Page):
    photo = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    bio = RichTextField(blank=True, null=True)
    website = models.URLField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('bio'),
        FieldPanel('website'),
        ImageChooserPanel('photo'),
    ]


class QuickFact(Orderable):
    page = ParentalKey('common.CategoryPage', related_name='quick_facts')
    body = RichTextField(validators=[validate_template])
    link_url = models.URLField(blank=True)


class StatisticsItem(Orderable):
    page = ParentalKey('common.CategoryPage', related_name='statistics_items')
    label = models.CharField(max_length=255)
    dataset = models.CharField(max_length=255, choices=get_numbers_choices())
    params = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Whitespace-separated list of arguments to be passed to the statistics function',
    )
    panels = [
        FieldPanel('label'),
        FieldPanel('dataset'),
        FieldPanel('params'),
    ]

    def clean(self):
        validate_dataset_params(self.dataset, self.params)


class TaxonomyCategoryPage(Orderable):
    taxonomy_setting = ParentalKey('common.TaxonomySettings', related_name='categories')
    category = ParentalKey('common.CategoryPage', related_name='taxonomy_settings')

    panels = [
        PageChooserPanel('category', 'common.CategoryPage'),
    ]


class CategoryIncidentFilter(Orderable):
    category = ParentalKey('common.CategoryPage', related_name='incident_filters')
    incident_filter = models.CharField(
        choices=IncidentFilter.get_filter_choices(),
        max_length=255,
        unique=True,
    )

    def clean(self):
        from common.models.settings import GeneralIncidentFilter
        if GeneralIncidentFilter.objects.filter(incident_filter=self.incident_filter).exists():
            raise ValidationError({
                'incident_filter': '"{}" is already in use in general filters'.format(
                    self.get_incident_filter_display(),
                ),
            })


class CategoryPage(MetadataPageMixin, Page):
    methodology = RichTextField(blank=True, validators=[validate_template])
    plural_name = models.CharField(max_length=255, null=True, blank=True)
    page_color = models.CharField(max_length=255, choices=CATEGORY_COLOR_CHOICES, default='eastern-blue')

    content_panels = Page.content_panels + [
        FieldPanel('methodology'),
        InlinePanel('quick_facts', label='Quick Facts'),
        InlinePanel('statistics_items', label='Statistics'),
        InlinePanel('incident_filters', label='Fields to include in filters'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('plural_name'),
        FieldPanel('page_color'),
    ]

    def get_context(self, request):
        # placed here to avoid circular dependency
        from incident.utils.incident_filter import IncidentFilter, get_serialized_filters
        from common.models.settings import SearchSettings

        context = super(CategoryPage, self).get_context(request)

        # request.is_preview is not necessarily set
        if getattr(request, 'is_preview', False):
            context['total_incidents'] = 'NOT AVAILABLE IN PREVIEW'
        else:
            context['total_incidents'] = self.incidents.filter(
                incident_page__live=True,
            ).count()

        data = request.GET.copy()
        data['categories'] = str(self.id)
        incident_filter = IncidentFilter(data)
        context['serialized_filters'] = json.dumps(get_serialized_filters())

        search_page = SearchSettings.for_site(request.site).search_page
        context['export_path'] = getattr(search_page, 'url', None)

        incident_qs = incident_filter.get_queryset()

        paginator, entries = paginate(
            request,
            incident_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=8,
            orphans=5
        )

        context['entries_page'] = entries
        context['paginator'] = paginator
        context['summary_table'] = incident_filter.get_summary()

        #  check if filters other than category are applied
        filters = dict(request.GET)
        filters.pop('page', None)
        filters.pop('categories', None)
        context['filtered'] = bool(filters)

        if request.is_ajax():
            context['layout_template'] = 'base.ajax.html'
        else:
            context['layout_template'] = 'base.html'

        context['data_items'] = [
            {
                'label': item.label,
                'value': render_as_template('{{% {tag_name}{params} %}}'.format(
                    tag_name=item.dataset,
                    params=' ' + item.params if item.params else '',
                )),
            } for item in self.statistics_items.all()
        ]
        return context

    def get_cache_tag(self):
        return 'category-page-{}'.format(self.pk)

    def serve(self, request, *args, **kwargs):
        """
        We set a cache tag here so that elsewhere we can purge all subroutes
        of the category page (including paginated and filtered URLs)
        simultaneously

        """

        response = super(CategoryPage, self).serve(request, *args, **kwargs)
        response['Cache-Tag'] = self.get_cache_tag()
        return response


class SimplePage(MetadataPageMixin, Page):
    body = StreamField([
        ('text', StyledTextTemplateBlock(label='Text', template='common/blocks/styled_text_full_bleed.html')),
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
        ('email_signup', EmailSignupBlock()),
    ])

    sidebar_content = StreamField(
        [
            ('heading', Heading2()),
            ('rich_text', blocks.RichTextBlock()),
        ],
        default=None,
        blank=True,
        null=True
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        StreamFieldPanel('sidebar_content')
    ]

    def get_context(self, request):
        # Avoid circular import
        from home.models import HomePage

        context = super(SimplePage, self).get_context(request)

        home = Page.objects.all().live().type(
            HomePage)[0]

        context['home_page'] = home

        return context

    def get_meta_description(self):
        if self.search_description:
            return self.search_description

        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )


class SimplePageWithSidebar(BaseSidebarPageMixin, MetadataPageMixin, Page):
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
        ('email_signup', EmailSignupBlock()),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    settings_panels = Page.settings_panels + BaseSidebarPageMixin.settings_panels

    def get_meta_description(self):
        if self.search_description:
            return self.search_description

        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )


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

    class Meta:
        ordering = ['title']
