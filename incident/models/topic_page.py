from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.http import JsonResponse
from marshmallow import Schema, fields
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    StreamFieldPanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.core import blocks
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailautocomplete.edit_handlers import AutocompletePanel

import common.blocks
from common.models import MetadataPageMixin, CategoryPage
from common.utils import (
    DEFAULT_PAGE_KEY,
    paginate,
)
from incident.models import IncidentCategorization


class IncidentSchema(Schema):
    title = fields.Str()
    date = fields.DateTime()
    url = fields.Function(lambda obj: obj.get_full_url())
    image = fields.Method('get_image')
    description = fields.Method('get_description')

    def get_image(self, obj):
        site = obj.get_site()
        if obj.teaser_image and site.root_url:
            return site.root_url + obj.teaser_image.get_rendition('width-720').url
        else:
            return ''

    def get_description(self, obj):
        return obj.body.render_as_block()


class CategorySchema(Schema):
    category = fields.Str(attribute='title')
    category_plural = fields.Str(attribute='plural_name')
    color = fields.Str(attribute='page_color')
    methodology = fields.Str()
    url = fields.Function(lambda obj: obj.get_full_url())
    total_incidents = fields.Int()
    total_journalists = fields.Int()
    incidents = fields.Method('get_incidents')

    def get_incidents(self, obj):
        incidents_schema = IncidentSchema(many=True)
        return incidents_schema.dump(
            [categorization.incident_page for categorization in obj.categorization_list]
        )


class TopicPage(RoutablePageMixin, MetadataPageMixin, Page):
    TOP_LEFT = 'top-left'
    BOTTOM_LEFT = 'bottom-left'
    TOP_CENTER = 'top-center'
    BOTTOM_CENTER = 'bottom-center'

    TEXT_ALIGN_CHOICES = (
        (TOP_CENTER, 'Top Center'),
        (BOTTOM_CENTER, 'Bottom Center'),
        (TOP_LEFT, 'Top Left'),
        (BOTTOM_LEFT, 'Bottom Left'),
    )

    WHITE = 'white'
    BLACK = 'black'
    TEXT_COLOR_CHOICES = (
        (WHITE, 'White'),
        (BLACK, 'Black'),
    )

    BY_INCIDENT = 'by_incident'
    BY_CATEGORY = 'by_category'
    LAYOUT_CHOICES = (
        (BY_INCIDENT, 'By Incident'),
        (BY_CATEGORY, 'By Category'),
    )

    superheading = models.TextField(
        help_text='Text that appears above the title in the heading block',
        blank=True,
        null=True
    )
    description = RichTextField(
        features=['bold', 'italic', 'link'],
        blank=True
    )
    text_align = models.CharField(
        max_length=255, choices=TEXT_ALIGN_CHOICES, default=BOTTOM_CENTER,
        help_text='Alignment of the full header text within the header image'
    )
    text_color = models.CharField(
        max_length=255, choices=TEXT_COLOR_CHOICES, default=WHITE,
        help_text='Color of header text, for legibility against the background.'
    )
    photo_caption = RichTextField(
        features=['bold', 'italic', 'link'],
        blank=True
    )
    photo_credit = models.TextField(blank=True)
    photo_credit_link = models.URLField(blank=True, null=True)
    photo = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    layout = models.CharField(
        max_length=255,
        choices=LAYOUT_CHOICES,
        default=BY_INCIDENT
    )
    incidents_per_module = models.PositiveIntegerField(
        default=4,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(3)
        ],
        help_text='Maximum incidents per category module in category layout'
    )

    content = StreamField([
        ('heading_2', common.blocks.Heading2()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('rich_text', blocks.RichTextBlock()),
        ('tweet', common.blocks.TweetEmbedBlock()),
        ('tabs', common.blocks.TabbedBlock()),
    ], blank=True)
    sidebar = StreamField([
        ('heading_2', common.blocks.Heading2()),
        ('rich_text', common.blocks.RichTextTemplateBlock(
            features=['bold', 'italic', 'link', 'ol', 'ul'],
            icon='doc-full',
            label='Rich Text',
        )),
        ('tweet', common.blocks.TweetEmbedBlock()),
        ('stat_table', common.blocks.StatTableBlock()),
        ('button', common.blocks.ButtonBlock()),
    ], blank=True)

    incident_index_page = models.ForeignKey(
        'incident.IncidentIndexPage',
        on_delete=models.PROTECT,
        related_name='+'
    )
    incident_tag = models.ForeignKey('common.CommonTag', on_delete=models.PROTECT)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            heading='Header',
            children=[
                FieldPanel('superheading'),
                FieldPanel('description'),
                FieldPanel('text_align'),
                FieldPanel('text_color'),
                ImageChooserPanel('photo'),
                FieldPanel('photo_caption'),
                FieldPanel('photo_credit'),
                FieldPanel('photo_credit_link'),
            ],
            classname='collapsible'
        ),
        MultiFieldPanel(
            heading='Statboxes',
            children=[
                InlinePanel('statboxes', label='Statboxes'),
            ],
            classname='collapsible',
        ),
        MultiFieldPanel(
            heading='Content',
            children=[
                StreamFieldPanel('content'),
                StreamFieldPanel('sidebar'),
            ],
            classname='collapsible',
        ),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            heading='Incidents',
            children=[
                PageChooserPanel('incident_index_page'),
                AutocompletePanel('incident_tag', page_type='common.CommonTag'),
                FieldPanel('incidents_per_module'),
            ],
            classname='collapsible',
        ),
        FieldPanel('layout'),
    ]

    def get_context(self, request):
        context = super(TopicPage, self).get_context(request)

        incident_qs = self.incident_index_page.get_incidents().filter(
            tags=self.incident_tag
        ).order_by('-date')

        paginator, entries = paginate(
            request,
            incident_qs,
            page_key=DEFAULT_PAGE_KEY,
            per_page=8,
            orphans=5
        )

        context['statboxes'] = self.statboxes.all()
        context['entries_page'] = entries
        context['paginator'] = paginator

        return context

    def get_categories_data(self):
        journalist_count = CategoryPage.objects.annotate(
            total_journalists=models.Count(
                'incidents__incident_page__targeted_journalists__journalist',
                filter=models.Q(
                    incidents__incident_page__tags=self.incident_tag,
                    incidents__incident_page__live=True,
                ),
                distinct=True,
            )
        ).filter(
            pk=models.OuterRef('pk')
        ).live()

        with_incident_page = IncidentCategorization.objects.select_related('incident_page').filter(
            id__in=models.Subquery(
                IncidentCategorization.objects.filter(
                    incident_page__tags=self.incident_tag,
                    category=models.OuterRef('category_id')
                ).order_by('-incident_page__date').values_list('id', flat=True)[:self.incidents_per_module]
            )
        ).order_by('-incident_page__date')

        cats = CategoryPage.objects.live().prefetch_related(
            models.Prefetch('incidents', queryset=with_incident_page, to_attr='categorization_list')
        ).annotate(
            total_journalists=models.Subquery(journalist_count.values('total_journalists'), output_field=models.IntegerField()),
            total_incidents=models.Count('incidents__incident_page', filter=models.Q(incidents__incident_page__tags=self.incident_tag, incidents__incident_page__live=True))
        ).order_by('-total_incidents')

        categories_schema = CategorySchema(many=True)
        result = categories_schema.dump(cats)
        return result

    @route('incidents/')
    def incidents_view(self, request):
        return JsonResponse(data=self.get_categories_data(), safe=False)
