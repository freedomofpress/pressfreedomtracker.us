import dataclasses
import datetime
import uuid

from django import forms
from django.db import models
from django.db.models import (
    Case,
    ExpressionWrapper,
    Max,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import ExtractDay, Cast, Trunc, TruncMonth, Coalesce, Concat
from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.template.defaultfilters import truncatewords
from modelcluster.fields import ParentalManyToManyField, ParentalKey
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.aggregates import ArrayAgg, StringAgg
from psycopg2.extras import DateRange
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail import blocks
from wagtail.fields import StreamField, RichTextField
from wagtail.models import Page, Orderable, PageManager, PageQuerySet
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index
from wagtailautocomplete.edit_handlers import AutocompletePanel
from common.blocks import (
    RichTextBlockQuoteBlock,
    AlignedCaptionedEmbedBlock,
    AlignedCaptionedImageBlock,
    TweetEmbedBlock,
    RichTextTemplateBlock,
    PullQuoteBlock,
)
from common.models import MetadataPageMixin
from incident import choices
from incident.models.category_fields import CATEGORY_FIELD_MAP, CAT_FIELD_VALUES
from incident.models.inlines import (
    IncidentPageUpdates,
    ChargeUpdate,
    IncidentCharge,
    LegalOrder,
    LegalOrderUpdate,
)
from incident.models.items import TargetedJournalist
from incident.circuits import CIRCUITS_BY_STATE
from incident.utils.db import CurrentDate, MakeDateRange, Left
from statistics.blocks import StatisticsBlock
from geonames.cities import get_city_coords


class IncidentAuthor(Orderable):
    parent_page = ParentalKey('IncidentPage', related_name='authors')
    author = models.ForeignKey('common.PersonPage', on_delete=models.CASCADE, related_name='+')

    @property
    def summary(self):
        return self.author.title

    panels = [
        FieldPanel('author')
    ]


@dataclasses.dataclass
class TargetLink:
    text: str
    url_arguments: str


class CheckboxMultipleChoice(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple


class ChoiceArrayField(ArrayField):
    """
    A field that allows us to store an array of choices.
    """

    def formfield(self, **kwargs):
        defaults = {
            'form_class': CheckboxMultipleChoice,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


def most_recent_status_of_charges_subquery():
    """Return a subquery that will evaluate to a comma-separated
    string containing every charge's most recent status.

    """
    newest_update = ChargeUpdate.objects.filter(
        incident_charge=OuterRef('pk'),
        date__gte=OuterRef('date')
    ).order_by('-date').values('status')[:1]

    latest_status = IncidentCharge.objects.filter(
        pk=OuterRef('pk'),
    ).annotate(
        newest_update=Subquery(newest_update),
        latest_status=Coalesce('newest_update', 'status'),
        latest_status_label=annotation_for_choices_display(
            'latest_status',
            choices.STATUS_OF_CHARGES,
        ),
    ).values('latest_status_label')

    charges_with_latest_status = IncidentCharge.objects.filter(
        incident_page=OuterRef('pk'),
    ).values(
        'incident_page__pk',
    ).annotate(
        latest_status=StringAgg(
            expression=latest_status,
            delimiter=', ',
        )
    ).values('latest_status')

    return Subquery(charges_with_latest_status)


class IncidentQuerySet(PageQuerySet):
    """A QuerySet for incident pages that incorporates update data"""
    def for_csv(self, with_annotations, request):
        from .incident_index_page import IncidentIndexPage
        # TODO: if 'url' in with_annotations, get the actually correct
        # base URI for the incident index page.
        base_uri = request.build_absolute_uri('/')
        available_annotations = {
            'tag_summary': Subquery(
                IncidentPage.objects.only('tags').annotate(
                    tag_summary=StringAgg(
                        'tags__title',
                        delimiter=', ',
                        ordering=('tags__title',)
                    )
                ).filter(
                    pk=OuterRef('pk')
                ).values('tag_summary'),
                output_field=models.CharField()
            ),
            'status_of_charges_summary': most_recent_status_of_charges_subquery(),
            'equipment_broken_summary': Subquery(
                IncidentPage.objects.only('equipment_broken').annotate(
                    equipment_broken_summary=StringAgg(
                        expression=Concat(
                            'equipment_broken__equipment__name',
                            Value(': count of '),
                            'equipment_broken__quantity',
                            output_field=models.CharField(),
                        ),
                        delimiter=', '
                    ),
                ).filter(
                    pk=OuterRef('pk'),
                ).values('equipment_broken_summary'),
            ),
            'equipment_seized_summary': Subquery(
                IncidentPage.objects.only('equipment_seized').annotate(
                    equipment_seized_summary=StringAgg(
                        expression=Concat(
                            'equipment_seized__equipment__name',
                            Value(': count of '),
                            'equipment_seized__quantity',
                            output_field=models.CharField(),
                        ),
                        delimiter=', '
                    ),
                ).filter(
                    pk=OuterRef('pk'),
                ).values('equipment_seized_summary'),
            ),
            'link_summary': Subquery(
                IncidentPage.objects.only('links').annotate(
                    link_summary=StringAgg(
                        expression=Concat(
                            'links__title',
                            Value(' ('),
                            'links__url',
                            Value(')'),
                            Case(
                                When(
                                    links__publication__isnull=True,
                                    then=Value(''),
                                ),
                                default=Concat(
                                    Value(' via '),
                                    'links__publication',
                                ),
                            ),
                            output_field=models.CharField(),
                        ),
                        delimiter=', ',
                    )
                ).filter(
                    pk=OuterRef('pk')
                ).values('link_summary'),
                output_field=models.CharField()
            ),
            'category_summary': Subquery(
                IncidentPage.objects.only('categories').annotate(
                    category_summary=StringAgg(
                        'categories__category__title',
                        delimiter=', ',
                        ordering=('categories__category__title',)
                    )
                ).filter(
                    pk=OuterRef('pk')
                ).values('category_summary'),
                output_field=models.CharField(),
            ),
            'url': Concat(
                Value(base_uri),
                Subquery(
                    IncidentIndexPage.objects.only('slug').filter(
                        depth=OuterRef('depth') - Value(1),
                        path=Left(OuterRef('path'), -1 * Page.steplen),
                    ).values('slug'),
                    output_field=models.CharField(),
                ),
                Value('/'),
                "slug",
                Value('/'),
                output_field=models.CharField()
            ),
            'state_abbreviation': models.F('state__abbreviation'),
            'arresting_authority_title': models.F('arresting_authority__title'),
            'status_of_seized_equipment_display': annotation_for_choices_display(
                'status_of_seized_equipment', choices.STATUS_OF_SEIZED_EQUIPMENT
            ),
            'arrest_status_display': annotation_for_choices_display(
                'arrest_status', choices.ARREST_STATUS,
            ),
            'actor_display': annotation_for_choices_display(
                'actor', choices.ACTORS,
            ),
            'target_us_citizenship_status_display': annotation_for_choices_display(
                'target_us_citizenship_status', choices.CITIZENSHIP_STATUS_CHOICES,
            ),
            'did_authorities_ask_for_device_access_display': annotation_for_choices_display(
                'did_authorities_ask_for_device_access', choices.MAYBE_BOOLEAN,
            ),
            'did_authorities_ask_about_work_display': annotation_for_choices_display(
                'did_authorities_ask_about_work', choices.MAYBE_BOOLEAN,
            ),
            'assailant_display': annotation_for_choices_display(
                'assailant', choices.ACTORS,
            ),
            'was_journalist_targeted_display': annotation_for_choices_display(
                'was_journalist_targeted', choices.MAYBE_BOOLEAN,
            ),
            'third_party_business_display': annotation_for_choices_display(
                'third_party_business', choices.ThirdPartyBusiness.choices,
            ),
            'status_of_prior_restraint_display': annotation_for_choices_display(
                'status_of_prior_restraint', choices.STATUS_OF_PRIOR_RESTRAINT,
            ),
            'legal_order_venue_display': annotation_for_choices_display(
                'legal_order_venue', choices.LegalOrderVenue.choices,
            ),
        }
        annotations_to_apply = {
            label: expression for label, expression in available_annotations.items()
            if label in with_annotations
        }
        return self.annotate(**annotations_to_apply)

    def with_public_associations(self):
        """Prefetch and select related data for public consumption

        This method gathers most incident-related data that we display
        on public pages and endpoints.  The goal is to avoid N+1
        queries when displaying many incidents at once.

        """
        return self.select_related(
            'teaser_image',
            'state',
            'arresting_authority'
        ).prefetch_related(
            'authors__author',
            'categories__category',
            models.Prefetch(
                'charges',
                queryset=IncidentCharge.objects.select_related('charge').prefetch_related('updates'),
            ),
            'equipment_broken__equipment',
            'equipment_seized__equipment',
            'links',
            'politicians_or_public_figures_involved',
            'tags',
            'target_nationality',
            'targeted_institutions',
            models.Prefetch('targeted_journalists', queryset=TargetedJournalist.objects.select_related('journalist', 'institution')),
            'teaser_image__renditions',
            'updates',
            'venue',
            'workers_whose_communications_were_obtained',
        )

    def with_most_recent_update(self):
        updates = IncidentPageUpdates.objects.filter(
            page=OuterRef('pk')
        ).order_by().values('page').annotate(
            most_recent_update=Max('date')
        ).values('most_recent_update')
        return self.annotate(
            # This is not super-efficient, as it runs the subquery
            # twice.  Need to evaluate if there's a better way.
            latest_update=ExpressionWrapper(Subquery(updates), output_field=models.DateField()),
            updated_days_ago=ExtractDay(ExpressionWrapper(
                CurrentDate() - Subquery(updates), output_field=models.DateField())
            ),
        )

    def updated_within_days(self, days):
        return self.with_most_recent_update().filter(
            updated_days_ago__lte=days
        )

    def with_most_recent_status_of_charges(self):
        """Annotate each incident with an array containing every
        charge's most recent status."""
        newest_update = ChargeUpdate.objects.filter(
            incident_charge=OuterRef('pk'),
            date__gte=OuterRef('date')
        ).order_by('-date').values('status')[:1]

        latest_status = IncidentCharge.objects.filter(
            pk=OuterRef('pk'),
        ).annotate(
            newest_update=Subquery(newest_update),
            latest_status=Coalesce('newest_update', 'status'),
        ).values('latest_status')

        charges_with_latest_status = IncidentCharge.objects.filter(
            incident_page=OuterRef('pk'),
        ).values(
            'incident_page__pk',
        ).annotate(
            latest_status=ArrayAgg(latest_status)
        ).values('latest_status')

        return self.annotate(
            most_recent_charge_statuses=Subquery(charges_with_latest_status),
        )

    def with_most_recent_status_of_legal_orders(self):
        """Annotate each incident with an array containing every
        legal order's most recent status."""
        newest_update = LegalOrderUpdate.objects.filter(
            legal_order=OuterRef('pk'),
        ).order_by('-sort_order').values('status')[:1]

        latest_status = LegalOrder.objects.filter(
            pk=OuterRef('pk'),
        ).annotate(
            newest_update=Subquery(newest_update),
            latest_status=Coalesce('newest_update', 'status'),
        ).values('latest_status')

        legal_orders_with_latest_status = LegalOrder.objects.filter(
            incident_page=OuterRef('pk'),
        ).values(
            'incident_page__pk',
        ).annotate(
            latest_status=ArrayAgg(latest_status)
        ).values('latest_status')

        return self.annotate(
            most_recent_legal_order_statuses=Subquery(
                legal_orders_with_latest_status
            ),
        )

    def fuzzy_date_filter(self, lower=None, upper=None):
        """Filter incidents by date range, accounting for unknown exact dates.

        This method accepts a date range and returns a queryset
        filtered according to the following algorithm:

        1. If an incident has `exact_date_unknown` equal to `False`,
        then the incident is included if the date range contains the
        incident's `date` value.

        2. If an incident has `exact_date_unknown` equal to `True`,
        then the incident is included if the date range overlaps with
        the month containing the incident's `date` value.  For
        example, if an exact date unknown incident has a date of
        2022-01-13 (or any other date in the month 2022-01), then it
        will be included in the queryset results if the date range
        overlaps at all with the range starting on 2022-01-01 and
        ending on 2022-01-31.

        3. Otherwise, the incident is excluded.

        Keyword arguments:
        lower -- the lower bound of the date (which is included in the range). If `None`, then the range is unbounded below.
        upper -- the lower bound of the date (which is included in the range). If `None`, then the range is unbounded below.

        """
        target_range = DateRange(
            lower=datetime.date.fromisoformat(str(lower)) if lower is not None else None,
            upper=datetime.date.fromisoformat(str(upper)) if upper is not None else None,
            bounds='[]',
        )
        exact_date_match = Q(
            date__contained_by=target_range,
            exact_date_unknown=False,
        )
        inexact_date_match = Q(
            exact_date_unknown=True,
            fuzzy_date__overlap=target_range,
        )
        return self.annotate(
            fuzzy_date=MakeDateRange(
                Cast(Trunc('date', 'month'), models.DateField()),
                Cast(TruncMonth('date') + Cast(Value('1 month'), models.DurationField()), models.DateField()),
            )
        ).filter(exact_date_match | inexact_date_match)


IncidentPageManager = PageManager.from_queryset(IncidentQuerySet)


class IncidentPage(MetadataPageMixin, Page):
    date = models.DateField()
    unique_date = models.TextField(unique=True)

    exact_date_unknown = models.BooleanField(
        default=False,
        help_text='If checked, only the month and year of the incident will be displayed. The date above will be used in filtering by date.'
    )

    city = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )
    state = models.ForeignKey(
        'incident.State',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text='Full name of the state. Abbreviations can be added in the Snippets editor.',
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    body = StreamField([
        ('rich_text', RichTextTemplateBlock(
            icon='doc-full',
            label='Rich Text',
        )),
        ('image', ImageChooserBlock(
            template='common/blocks/image_block.html'
        )),
        ('aligned_image', AlignedCaptionedImageBlock(
            label='Aligned, Captioned Image',
        )),
        ('raw_html', blocks.RawHTMLBlock()),
        ('tweet', TweetEmbedBlock()),
        ('blockquote', RichTextBlockQuoteBlock()),
        ('pull_quote', PullQuoteBlock()),
        ('video', AlignedCaptionedEmbedBlock()),
        ('statistics', StatisticsBlock()),
    ], use_json_field=True)

    introduction = models.TextField(
        help_text="Optional: introduction displayed above the image.",
        blank=True,
        null=True,
    )

    teaser = models.TextField(
        help_text="This field is optional and overrides the default teaser text.",
        blank=True,
        null=True,
        max_length=384,
    )

    teaser_image = models.ForeignKey(
        'common.CustomImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    primary_video = models.URLField(
        blank=True,
        null=True,
        help_text='YouTube or Vimeo URL'
    )

    image_caption = RichTextField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Image description displayed below the image. Organization/Photographer can be set via the image attribution.'
    )

    targeted_institutions = ParentalManyToManyField(
        'incident.Institution',
        blank=True,
        verbose_name='Targeted Institutions',
        related_name='institutions_incidents',
    )

    tags = ParentalManyToManyField(
        'common.CommonTag',
        blank=True,
        verbose_name='Tags',
        related_name='tagged_items',
    )

    # This field can be used to suppress the default CTA text, in case the body already
    # contains the CTA text. One can just check this, to suppress the text.
    suppress_footer = models.BooleanField(
        default=False,
        verbose_name='Suppress Footer Call to Action',
        help_text='This field will suppress call to action text. If body already contains cta, can check this field.'
    )

    related_incidents = ParentalManyToManyField('self', blank=True)

    # Detention/Arrest
    arrest_status = models.CharField(
        choices=choices.ARREST_STATUS,
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Arrest status'
    )
    status_of_charges = models.CharField(
        choices=choices.STATUS_OF_CHARGES,
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Status of charges'
    )
    arresting_authority = models.ForeignKey(
        'incident.LawEnforcementOrganization',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        help_text='Arresting authority.',
    )
    current_charges = ParentalManyToManyField(
        'incident.Charge',
        blank=True,
        related_name='current_charge_incidents',
        verbose_name='Current Charges',
    )
    dropped_charges = ParentalManyToManyField(
        'incident.Charge',
        blank=True,
        related_name='dropped_charge_incidents',
        verbose_name='Dropped Charges',
    )
    release_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Release date'
    )
    detention_date = models.DateField(
        blank=True,
        null=True,
        help_text='This field will default to the date field if not specified.',
        verbose_name="Detention date"
    )
    unnecessary_use_of_force = models.BooleanField(
        default=False,
        verbose_name='Unnecessary use of force?'
    )

    # Legal Case

    # DEPRECATION WARNING!
    # PS: Delete lawsuit_name and venue fields in a month.
    lawsuit_name = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name='Lawsuit name'
    )
    venue = ParentalManyToManyField(
        'incident.Venue',
        blank=True,
        verbose_name='Case Venue',
        related_name='venue_incidents',
        help_text='Courts that are hearing or have heard this case.'
    )

    case_number = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name='Case number'
    )
    case_statuses = ChoiceArrayField(
        models.CharField(
            max_length=255,
            choices=choices.CASE_STATUS,
        ),
        blank=True,
        null=True,
        verbose_name="Legal case statuses"
    )
    case_type = models.CharField(
        choices=choices.CASE_TYPE,
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Type of case"
    )

    # Equipment Seizure or Damage
    status_of_seized_equipment = models.CharField(
        choices=choices.STATUS_OF_SEIZED_EQUIPMENT,
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Status of seized equipment"
    )
    is_search_warrant_obtained = models.BooleanField(
        default=False,
        verbose_name="Search warrant obtained?"
    )
    actor = models.CharField(
        choices=choices.ACTORS,
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Actor"
    )

    # Border Stop/Denial of Entry
    border_point = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Border point'
    )
    target_us_citizenship_status = models.CharField(
        choices=choices.CITIZENSHIP_STATUS_CHOICES,
        max_length=255,
        blank=True,
        null=True,
        verbose_name="US Citizenship Status"
    )
    denial_of_entry = models.BooleanField(
        default=False,
        verbose_name='Denied entry?'
    )
    stopped_previously = models.BooleanField(
        default=False,
        verbose_name='Stopped previously?'
    )
    target_nationality = ParentalManyToManyField(
        'incident.Nationality',
        blank=True,
        related_name='nationality_incidents',
        verbose_name='Target Nationality',
    )
    did_authorities_ask_for_device_access = models.CharField(
        choices=choices.MAYBE_BOOLEAN,
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Did authorities ask for device access?"
    )
    did_authorities_ask_for_social_media_user = models.CharField(
        choices=choices.MAYBE_BOOLEAN,
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Did authorities ask for social media username?"
    )
    did_authorities_ask_for_social_media_pass = models.CharField(
        choices=choices.MAYBE_BOOLEAN,
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Did authorities ask for social media password?"
    )
    did_authorities_ask_about_work = models.CharField(
        choices=choices.MAYBE_BOOLEAN,
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Did authorities ask intrusive questions about journalist\'s work?',
    )
    were_devices_searched_or_seized = models.CharField(
        choices=choices.MAYBE_BOOLEAN,
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Were devices searched or seized?'
    )

    # Physical Assault
    assailant = models.CharField(
        choices=choices.ACTORS,
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Assailant"
    )
    was_journalist_targeted = models.CharField(
        choices=choices.MAYBE_BOOLEAN,
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Was journalist targeted?"
    )

    # Leak Prosecution
    workers_whose_communications_were_obtained = ParentalManyToManyField(
        'incident.GovernmentWorker',
        verbose_name='Targets whose communications were obtained in leak investigation',
        related_name='incidents',
        blank=True,
    )
    charged_under_espionage_act = models.BooleanField(
        default=False,
        verbose_name="Charged under espionage act?"
    )

    # Subpoena of Journalism
    subpoena_type = models.CharField(
        choices=choices.SUBPOENA_TYPE,
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Subpoena type"
    )
    subpoena_statuses = ChoiceArrayField(
        models.CharField(
            max_length=255,
            choices=choices.SUBPOENA_STATUS,
        ),
        blank=True,
        null=True,
        verbose_name="Subpoena statuses"
    )

    # Deprecated field.
    held_in_contempt = models.CharField(
        choices=choices.MAYBE_BOOLEAN,
        max_length=255,
        blank=True,
        null=True,
        verbose_name='If subject refused to cooperate, were they held in contempt?',
    )

    # Deprecated field.
    detention_status = models.CharField(
        choices=choices.DETENTION_STATUS,
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Detention status"
    )

    # Legal Order for Journalist's Records
    name_of_business = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name='Name of business',
        help_text='Name of the business targeted by legal order. This field is only displayed if the legal order target is set to "Third Party"',
    )
    third_party_business = models.CharField(
        choices=choices.THIRD_PARTY_BUSINESS,
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Third party business'
    )
    legal_order_target = models.CharField(
        choices=choices.LegalOrderTarget.choices,
        max_length=255,
        blank=True,
        null=True,
    )
    legal_order_type = models.CharField(
        choices=choices.LEGAL_ORDER_TYPE,
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Legal order type'
    )
    legal_order_venue = models.CharField(
        choices=choices.LegalOrderVenue.choices,
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Legal order venue',
    )

    # Prior Restraint
    status_of_prior_restraint = models.CharField(
        choices=choices.STATUS_OF_PRIOR_RESTRAINT,
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Status of prior restraint'
    )

    # Denial of Access
    politicians_or_public_figures_involved = ParentalManyToManyField(
        'incident.PoliticianOrPublic',
        blank=True,
        related_name='politicians_or_public_incidents',
        verbose_name='Government agency or public official involved',
    )

    objects = IncidentPageManager()

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            heading='Introduction, Video, Image and Teaser',
            children=[
                FieldPanel('introduction'),
                FieldPanel('primary_video'),
                FieldPanel('teaser_image'),
                FieldPanel('image_caption'),
                FieldPanel('teaser'),
            ]
        ),
        FieldPanel('body'),
        MultiFieldPanel(
            heading='Details',
            children=[
                FieldPanel('date'),
                FieldPanel('exact_date_unknown'),
                FieldPanel('city'),
                AutocompletePanel('state', target_model='incident.State'),
                InlinePanel('targeted_journalists', label='Targeted Journalists'),
                AutocompletePanel('targeted_institutions', 'incident.Institution'),
                AutocompletePanel('tags', 'common.CommonTag'),
                InlinePanel('categories', label='Incident categories', min_num=1),
            ]
        ),
        InlinePanel(
            'authors',
            label='Authors',
            help_text='Author pages must already exist.'
        ),
        InlinePanel('updates', label='Updates'),
        InlinePanel(
            'links',
            label='Sources',
            help_text="Links to resources and news articles related to this"
                      "incident. Displayed as footnotes."
        ),

        MultiFieldPanel(
            heading='Arrest/Criminal Charge',
            classname='collapsible collapsed',
            children=[
                AutocompletePanel('arresting_authority', target_model='incident.LawEnforcementOrganization'),
                FieldPanel('arrest_status'),
                InlinePanel('charges', label='Charges'),
                FieldPanel('status_of_charges'),
                AutocompletePanel('current_charges', 'incident.Charge'),
                AutocompletePanel('dropped_charges', 'incident.Charge'),
                FieldPanel('detention_date'),
                FieldPanel('release_date'),
                FieldPanel('unnecessary_use_of_force'),
            ]
        ),

        MultiFieldPanel(
            heading='Assault',
            classname='collapsible collapsed',
            children=[
                FieldPanel('assailant'),
                FieldPanel('was_journalist_targeted'),
            ]
        ),

        MultiFieldPanel(
            heading='Border Stop/Denial of Entry',
            classname='collapsible collapsed',
            children=[
                FieldPanel('border_point'),
                FieldPanel('target_us_citizenship_status'),
                FieldPanel('denial_of_entry'),
                FieldPanel('stopped_previously'),
                AutocompletePanel('target_nationality', 'incident.Nationality'),
                FieldPanel('did_authorities_ask_for_device_access'),
                FieldPanel('did_authorities_ask_for_social_media_user'),
                FieldPanel('did_authorities_ask_for_social_media_pass'),
                FieldPanel('did_authorities_ask_about_work'),
                FieldPanel('were_devices_searched_or_seized'),
            ]
        ),

        MultiFieldPanel(
            heading='Denial of Access',
            classname='collapsible collapsed',
            children=[
                AutocompletePanel('politicians_or_public_figures_involved', 'incident.PoliticianOrPublic'),
            ]
        ),

        MultiFieldPanel(
            heading='Equipment Damage',
            classname='collapsible collapsed',
            children=[
                FieldPanel('actor'),
                InlinePanel(
                    'equipment_broken',
                    label='Equipment',
                ),
            ],
        ),

        MultiFieldPanel(
            heading='Equipment Searched or Seized',
            classname='collapsible collapsed',
            children=[
                FieldPanel('status_of_seized_equipment'),
                FieldPanel('is_search_warrant_obtained'),
                InlinePanel(
                    'equipment_seized',
                    label='Equipment',
                ),
            ],
        ),

        MultiFieldPanel(
            heading='Leak Prosecution',
            classname='collapsible collapsed',
            children=[
                AutocompletePanel('workers_whose_communications_were_obtained', 'incident.GovernmentWorker'),
                FieldPanel('charged_under_espionage_act'),
            ]
        ),

        MultiFieldPanel(
            heading='Legal Case',
            classname='collapsible collapsed',
            children=[
                FieldPanel('case_number'),
                FieldPanel('case_statuses'),
                FieldPanel('case_type'),
            ]
        ),

        MultiFieldPanel(
            heading='Prior Restraint',
            classname='collapsible collapsed',
            children=[
                FieldPanel('status_of_prior_restraint'),
            ]
        ),

        MultiFieldPanel(
            heading='Subpoena/Legal Order',
            classname='collapsible collapsed',
            children=[
                FieldPanel('legal_order_type'),
                FieldPanel('legal_order_target'),
                FieldPanel('legal_order_venue'),
                InlinePanel('legal_orders', label='Legal Orders'),
                FieldPanel('third_party_business'),
                FieldPanel('name_of_business'),
            ]
        ),

        AutocompletePanel('related_incidents', 'incident.IncidentPage'),
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel('suppress_footer')
    ]

    parent_page_types = ['incident.IncidentIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('city'),
        index.RelatedFields('state', [
            index.SearchField('name'),
        ]),
        index.SearchField('introduction'),
        index.SearchField('teaser'),
        index.RelatedFields('teaser_image', [
            index.SearchField('attribution'),
        ]),
        index.SearchField('image_caption'),
        index.RelatedFields('updates', [
            index.SearchField('title'),
            index.SearchField('body'),
        ]),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(IncidentPage, self).get_context(request, *args, **kwargs)

        related_incidents = self.get_related_incidents(threshold=4)
        context['related_incidents'] = related_incidents

        main_category = self.get_main_category()
        context['main_category'] = main_category
        context['category_details'] = self.get_category_details()
        return context

    def full_clean(self, *args, **kwargs):
        if self.unique_date and self.unique_date[:10] != str(self.date):
            # if the date has been changed, only change the date part
            # of unique_date
            uuid_ = self.unique_date[11:]
            self.unique_date = f'{self.date}-{uuid_}'
        elif not self.unique_date:
            # create a new uuid for unique date if it's not present
            uuid_ = uuid.uuid1()
            self.unique_date = f'{self.date}-{uuid_}'

        super().full_clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.state:
            self.latitude, self.longitude = get_city_coords(self.city, self.state.abbreviation)
        return super(IncidentPage, self).save(*args, **kwargs)

    def detention_duration(self):
        """
        Returns the total duration of detention.
        If a detention_date is not explicitly provided, the incident date is
        used instead. The end date is either today, for a live duration, or
        the release_date, if specified.
        """
        start_date = self.detention_date if self.detention_date else self.date
        end_date = self.release_date if self.release_date else datetime.datetime.today()
        return end_date - start_date

    def last_updated(self):
        """
        Returns the date this incident was last updated on or the date of publication if no updates exist.
        """
        first = self.updates.order_by('-date').first()
        if first:
            return first.date
        return self.first_published_at

    def recently_updated(self):
        """
        Determines whether an incident has been updated within the last week. Returns a boolean.
        """
        if getattr(self, 'updated_days_ago', None) is not None:
            return self.updated_days_ago < 7
        else:
            latest_update = self.updates.order_by('-date').first()
            if latest_update:
                delta = datetime.datetime.now(datetime.timezone.utc) - latest_update.date
                return delta.days < 7
            return False

    def get_updates_by_asc_date(self):
        """
        Returns updates for the incident sorted in ascending order by date of update
        """
        return self.updates.order_by('date').all()

    def get_updates_by_desc_date(self):
        """
        Returns updates for the incident sorted in descending order by date of update
        """
        return self.updates.order_by('-date').all()

    def get_main_category(self):
        """
        Returns the first category in the list of categories
        """
        first_category = self.categories.all().first()
        if first_category:
            return first_category.category
        return None

    def get_category_details(self, index=None):
        if not index:
            index = self.get_parent()

        category_details = {}
        categories_without_metadata = {}
        for category in self.categories.all():
            category_fields = CATEGORY_FIELD_MAP.get(category.category.slug, [])

            if not category_fields:
                categories_without_metadata[category.category] = []
                continue
            category_details[category.category] = []
            for field in category_fields:
                display_html = CAT_FIELD_VALUES[field[0]](self, field[0], index, category.category)
                category_details[category.category].append(
                    {
                        'name': field[1],
                        'html': display_html,
                    }
                )
        category_details.update(categories_without_metadata)
        return category_details

    def get_related_incidents(self, threshold=4):
        """Locates related incidents using an incident's main category, tags
        and city/state as parameters.

        This function will query an incident's explicitly set
        `related_incidents` and always return that entire set.
        Additionally, it will supplement these with other incidents based
        matching data until a threshold number of incidents is met.
        Supplemental incidents are ranked based on overlapping tags and
        matching city and state values.

        """
        related_incidents = list(self.related_incidents.order_by('-date'))
        main_category = self.get_main_category()

        if len(related_incidents) >= threshold:
            return related_incidents

        exclude_ids = {incident.pk for incident in related_incidents}
        if self.pk:
            exclude_ids.add(self.pk)

        own_tags = [tag.pk for tag in self.get_tags]
        own_tags_set = set(own_tags)

        conditional_filter = Q(location_rank__gt=0)
        if own_tags:
            conditional_filter = Q(tag_array__overlap=own_tags) | Q(location_rank__gt=0)

        candidates = IncidentPage.objects.annotate(
            tag_array=ArrayAgg(
                'tags',
                filter=models.Q(tags__isnull=False)  # excludes results of `[None]`
            ),
            location_rank=Case(
                When(city=self.city, state=self.state, then=Value(2)),
                When(state=None, then=Value(0)),
                When(state=self.state, then=Value(1)),
                default=Value(0),
                output_field=(models.IntegerField())
            ),
        ).filter(
            Q(live=True),
            Q(categories__category=main_category),
            conditional_filter
        ).exclude(
            id__in=exclude_ids
        )

        def sorter(incident):
            if incident.tag_array:
                tag_rank = len(set(incident.tag_array) & own_tags_set)
            else:
                tag_rank = 0
            return (tag_rank, incident.location_rank, incident.date)

        candidates = sorted(candidates, reverse=True, key=sorter)

        related_incidents += candidates

        # Return what we have, even if it potentially does not meet
        # the threshold.
        return related_incidents[:threshold]

    def get_court_circuit(self):
        if self.state:
            for state, circuit in CIRCUITS_BY_STATE.items():
                if state == self.state.name:
                    return circuit
        return None

    def get_meta_image(self):
        return (
            self.teaser_image or
            self.search_image or
            (self.get_main_category() and self.get_main_category().default_image) or
            self._get_ssssettings().default_image
        )

    def get_meta_description(self):
        if self.teaser:
            return self.teaser

        if self.search_description:
            return self.search_description

        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )

    @cached_property
    def get_tags(self):
        return self.tags.all()

    @cached_property
    def get_all_targets_for_linking(self):
        items = []
        for tj in self.targeted_journalists.all():
            if tj.institution:
                title = f'{tj.journalist.title} ({tj.institution.title})'
            else:
                title = tj.journalist.title
            items.append(
                TargetLink(
                    text=title,
                    url_arguments=f'targeted_journalists={tj.journalist.title}'
                )
            )
        for institution in self.targeted_institutions.all():
            items.append(
                TargetLink(
                    text=institution.title,
                    url_arguments=f'targeted_institutions={institution.title}'
                )
            )
        return items

    @cached_property
    def get_all_targets_for_display(self):
        items = []
        targeted_journalists = (
            self.targeted_journalists
            .select_related('journalist', 'institution')
            .order_by('journalist__title')
            .all()
        )
        for tj in targeted_journalists:
            if tj.institution:
                items.append(f'{tj.journalist.title} ({tj.institution.title})')
            else:
                items.append(f'{tj.journalist.title}')
        for institution in self.targeted_institutions.all():
            items.append(f'{institution.title}')
        return ', '.join(items)


def annotation_for_choices_display(field_name, all_choices):
    """Return an SQL case statement for converting choice values
    (i.e. the strings stored in the database) to human-readable choice
    display values (which are typically stored in our Python code).

    """
    return Case(
        *[
            When(**{field_name: choice_value}, then=Value(choice_name))
            for choice_value, choice_name in all_choices
        ]
    )
