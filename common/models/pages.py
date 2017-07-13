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
    StyledTextBlock,
    AlignedCaptionedImageBlock,
    AlignedCaptionedEmbedBlock
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
            targets=request.GET.get('targets'),
            affiliation=request.GET.get('affiliation'),
            states=request.GET.get('states'),
            tags=request.GET.get('tags'),
            # ARREST / DETENTION
            arrest_status=request.GET.get('arrest_status'),
            status_of_charges=request.GET.get('status_of_charges'),
            current_charges=request.GET.get('current_charges'),
            dropped_charges=request.GET.get('dropped_charges'),
            # EQUIPMENT
            equipment_seized=request.GET.get('equipment_seized'),
            equipment_broken=request.GET.get('equipment_broken'),
            status_of_seized_equipment=request.GET.get('status_of_seized_equipment'),
            is_search_warrant_obtained=request.GET.get('is_search_warrant_obtained'),
            actor=request.GET.get('actors'),
            # BORDER STOP
            border_point=request.GET.get('border_point'),
            stopped_at_border=request.GET.get('stopped_at_border'),
            target_us_citizenship_status=request.GET.get('target_us_citizenship_status'),
            denial_of_entry=request.GET.get('denial_of_entry'),
            stopped_previously=request.GET.get('stopped_previously'),
            target_nationality=request.GET.get('target_nationality'),
            did_authorities_ask_for_device_access=request.GET.get('did_authorities_ask_for_device_access'),
            did_authorities_ask_for_social_media_user=request.GET.get('did_authorities_ask_for_social_media_user'),
            did_authorities_ask_for_social_media_pass=request.GET.get('did_authorities_ask_for_social_media_pass'),
            did_authorities_ask_about_work=request.GET.get('did_authorities_ask_about_work'),
            were_devices_searched_or_seized=request.GET.get('weredevices_searched_or_seized'),
            # PHYSICAL ASSAULT
            assailant=request.GET.get('assailant'),
            was_journalist_targeted=request.GET.get('was_journalist_targeted'),
            # LEAK PROSECUTION
            charged_under_espionage_act=request.GET.get('charged_under_espionage_act'),
            # SUBPOENA
            subpoena_subject=request.GET.get('subpoena_subject'),
            subpoena_type=request.GET.get('subpoena_type'),
            subpoena_status=request.GET.get('subpoena_status'),
            held_in_contempt=request.GET.get('held_in_contempt'),
            detention_status=request.GET.get('detention_status'),
            third_party_in_possession_of_communications=request.GET.get('third_party_in_possession_of_communications'),
            third_party_business=request.GET.get('third_party_business'),
            legal_order_type=request.GET.get('legal_order_type'),
            # PRIOR RESTRAINT
            status_of_prior_restraint=request.GET.get('status_of_prior_restraint'),
            # DENIAL OF ACCESS
            politicians_or_public_figures_involved=request.GET.get('politicians_or_public_figures_involved'),
        ).fetch()
        return context


class SimplePage(Page):
    body = StreamField([
        ('text', StyledTextBlock(label='Text', template='common/blocks/styled_text_full_bleed.html')),
        ('image', AlignedCaptionedImageBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('blockquote', blocks.BlockQuoteBlock()),
        ('list', blocks.ListBlock(
            blocks.CharBlock(label="List Item"),
            template='common/blocks/list_block_columns.html'
        )),
        ('video', AlignedCaptionedEmbedBlock()),
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
        ('text', StyledTextBlock(label='Text')),
        ('image', AlignedCaptionedImageBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('blockquote', blocks.BlockQuoteBlock()),
        ('list', blocks.ListBlock(
            blocks.CharBlock(label="List Item"),
            template='common/blocks/list_block_columns.html'
        )),
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
