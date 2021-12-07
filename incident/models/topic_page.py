from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import DateRangeField
from django.http import JsonResponse
from marshmallow import Schema, fields
from psycopg2.extras import DateRange
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
from incident.forms import TopicPageForm


class FuzzyDate(models.Transform):
    """Django lookup that transforms a single date into a date range of
    the month containing that date.

    """

    lookup_name = 'fuzzy_date'
    template = "daterange(date_trunc('month', %(expressions)s)::date, (date_trunc('month', %(expressions)s) + interval '1 month')::date)"

    @property
    def output_field(self):
        return DateRangeField()


models.DateField.register_lookup(FuzzyDate)


class NongroupingSubquery(models.Subquery):
    def get_group_by_cols(self):
        return []


class IncidentSchema(Schema):
    title = fields.Str()
    date = fields.DateTime()
    url = fields.Function(lambda obj: obj.get_full_url())
    image = fields.Method('get_image')
    description = fields.Method('get_description')

    def get_image(self, obj):
        if not obj.teaser_image:
            return ''
        val = ''
        for rend in obj.teaser_image.renditions.all():
            if rend.filter_spec == 'width-720':
                val = rend.url
        if not val:
            val = obj.teaser_image.get_rendition('width-720').url
        return val

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
            [categorization.incident_page for categorization in obj.categorization_list][:self.context['incident_limit']]
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
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text='Start date for this topic. No incidents before this date will be included.',
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text='End date for this topic. No incidents after this date will be included.',
    )

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
                AutocompletePanel('incident_tag', target_model='common.CommonTag'),
                FieldPanel('incidents_per_module'),
                FieldPanel('start_date'),
                FieldPanel('end_date'),
            ],
            classname='collapsible',
        ),
        FieldPanel('layout'),
    ]
    base_form_class = TopicPageForm

    def get_context(self, request, *args, **kwargs):
        context = super(TopicPage, self).get_context(request, *args, **kwargs)

        incident_lookups = models.Q(tags=self.incident_tag)
        if self.start_date or self.end_date:
            target_range = DateRange(
                lower=self.start_date,
                upper=self.end_date,
                bounds='[]',
            )

            incident_lookups &= (
                models.Q(date__contained_by=target_range) |
                models.Q(
                    exact_date_unknown=True,
                    date__fuzzy_date__overlap=target_range,
                )
            )
        incident_qs = self.incident_index_page.get_incidents().filter(
            incident_lookups
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
        incident_lookups = models.Q(
            incident_page__tags=self.incident_tag,
            incident_page__live=True,
        )
        category_incident_lookups = models.Q(
            incidents__incident_page__tags=self.incident_tag,
            incidents__incident_page__live=True,
        )
        if self.start_date or self.end_date:
            target_range = DateRange(
                lower=self.start_date,
                upper=self.end_date,
                bounds='[]',
            )

            incident_lookups &= (
                models.Q(incident_page__date__contained_by=target_range) |
                models.Q(
                    incident_page__exact_date_unknown=True,
                    incident_page__date__fuzzy_date__overlap=target_range,

                )
            )
            category_incident_lookups &= (
                models.Q(
                    incidents__incident_page__date__contained_by=target_range,
                ) | models.Q(
                    incidents__incident_page__exact_date_unknown=True,
                    incidents__incident_page__date__fuzzy_date__overlap=target_range,
                )
            )

        journalist_count = CategoryPage.objects.annotate(
            total_journalists=models.Count(
                'incidents__incident_page__targeted_journalists__journalist',
                filter=category_incident_lookups,
                distinct=True,
            )
        ).filter(
            pk=models.OuterRef('pk')
        ).live()

        categorization_with_incidents = IncidentCategorization.objects\
            .prefetch_related(
                'incident_page__teaser_image__renditions',
            ).select_related(
                'incident_page'
            ).filter(
                incident_lookups
            ).order_by('-incident_page__date')

        prefetch_categorizations = models.Prefetch(
            'incidents', queryset=categorization_with_incidents, to_attr='categorization_list'
        )

        cats = CategoryPage.objects.live().prefetch_related(
            prefetch_categorizations,
        ).annotate(
            total_journalists=NongroupingSubquery(journalist_count.values('total_journalists'), output_field=models.IntegerField()),
            total_incidents=models.Count('incidents__incident_page', filter=category_incident_lookups)
        ).order_by('-total_incidents')

        categories_schema = CategorySchema(many=True)
        categories_schema.context = {'incident_limit': self.incidents_per_module}
        result = categories_schema.dump(cats)
        return result

    @route('incidents/')
    def incidents_view(self, request):
        return JsonResponse(data=self.get_categories_data(), safe=False)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_date__lte=models.F('end_date')),
                name='start_date_end_date_order'
            ),
        ]
