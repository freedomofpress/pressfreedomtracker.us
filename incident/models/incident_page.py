import datetime
from urllib.parse import urlencode

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
from django.db.models.functions import ExtractDay
from django.utils.html import strip_tags
from django.template.defaultfilters import truncatewords
from modelcluster.fields import ParentalManyToManyField, ParentalKey
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.aggregates import ArrayAgg
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
    StreamFieldPanel,
)
from wagtail.core import blocks
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Page, Orderable, PageManager, PageQuerySet
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel

from wagtailautocomplete.edit_handlers import AutocompletePanel
from common.blocks import (
    RichTextBlockQuoteBlock,
    AlignedCaptionedEmbedBlock,
    AlignedCaptionedImageBlock,
    TweetEmbedBlock,
    RichTextTemplateBlock,
)
from common.models import MetadataPageMixin
from incident.models import choices
from incident.models.inlines import IncidentPageUpdates
from incident.models.items import TargetedJournalist
from incident.circuits import CIRCUITS_BY_STATE
from incident.utils.db import CurrentDate
from statistics.blocks import StatisticsBlock


class IncidentAuthor(Orderable):
    parent_page = ParentalKey('IncidentPage', related_name='authors')
    author = models.ForeignKey('common.PersonPage', on_delete=models.CASCADE, related_name='+')

    panels = [
        PageChooserPanel('author')
    ]


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


class IncidentQuerySet(PageQuerySet):
    """A QuerySet for incident pages that incorporates update data"""
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
            'current_charges',
            'dropped_charges',
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
            updated_days_ago=ExtractDay(ExpressionWrapper(
                CurrentDate() - Subquery(updates), output_field=models.DateField())
            ),
        )

    def updated_within_days(self, days):
        return self.with_most_recent_update().filter(
            updated_days_ago__lte=days
        )


IncidentPageManager = PageManager.from_queryset(IncidentQuerySet)


class IncidentPage(MetadataPageMixin, Page):
    date = models.DateField()

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

    body = StreamField([
        ('rich_text', RichTextTemplateBlock(
            icon='doc-full',
            label='Rich Text',
        )),
        ('image', ImageChooserBlock()),
        ('aligned_image', AlignedCaptionedImageBlock(
            label='Aligned, Captioned Image',
        )),
        ('raw_html', blocks.RawHTMLBlock()),
        ('tweet', TweetEmbedBlock()),
        ('blockquote', RichTextBlockQuoteBlock()),
        ('video', AlignedCaptionedEmbedBlock()),
        ('statistics', StatisticsBlock()),
    ])

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
    stopped_at_border = models.BooleanField(
        default=False,
        verbose_name="Stopped at border?"
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
    held_in_contempt = models.CharField(
        choices=choices.MAYBE_BOOLEAN,
        max_length=255,
        blank=True,
        null=True,
        verbose_name='If subject refused to cooperate, were they held in contempt?',
    )
    detention_status = models.CharField(
        choices=choices.DETENTION_STATUS,
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Detention status"
    )

    # Legal Order for Journalist's Records
    third_party_in_possession_of_communications = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name='Third party in possession of communications'
    )
    third_party_business = models.CharField(
        choices=choices.THIRD_PARTY_BUSINESS,
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Third party business'
    )
    legal_order_type = models.CharField(
        choices=choices.LEGAL_ORDER_TYPE,
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Legal order type'
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
        verbose_name='Politicians or public officials involved',
    )

    objects = IncidentPageManager()

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),

        MultiFieldPanel(
            heading='Teaser',
            children=[
                ImageChooserPanel('teaser_image'),
                FieldPanel('image_caption'),
                FieldPanel('teaser'),
            ]
        ),
        MultiFieldPanel(
            heading='Details',
            children=[
                FieldPanel('date'),
                FieldPanel('exact_date_unknown'),
                FieldPanel('city'),
                AutocompletePanel('state', page_type='incident.State'),
                InlinePanel('targeted_journalists', label='Targeted Journalists'),
                AutocompletePanel('targeted_institutions', 'incident.Institution', is_single=False),
                AutocompletePanel('tags', 'common.CommonTag', is_single=False),
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

        FieldPanel('primary_video'),

        MultiFieldPanel(
            heading='Detention/Arrest',
            classname='collapsible collapsed',
            children=[
                FieldPanel('arrest_status'),
                FieldPanel('status_of_charges'),
                AutocompletePanel('arresting_authority', page_type='incident.LawEnforcementOrganization'),
                AutocompletePanel('current_charges', 'incident.Charge', is_single=False),
                AutocompletePanel('dropped_charges', 'incident.Charge', is_single=False),
                FieldPanel('detention_date'),
                FieldPanel('release_date'),
                FieldPanel('unnecessary_use_of_force'),
            ]
        ),

        MultiFieldPanel(
            heading='Legal Case',
            classname='collapsible collapsed',
            children=[
                FieldPanel('lawsuit_name'),
                AutocompletePanel('venue', 'incident.Venue', is_single=False),
            ]
        ),

        # Not in an MFP because we want their headings to show up.
        InlinePanel(
            'equipment_seized',
            classname='collapsible collapsed',
            label='Equipment Searched or Seized',
        ),
        InlinePanel(
            'equipment_broken',
            classname='collapsible collapsed',
            label='Equipment Broken',
        ),

        MultiFieldPanel(
            heading='Equipment Seizure or Damage',
            classname='collapsible collapsed',
            children=[
                FieldPanel('status_of_seized_equipment'),
                FieldPanel('is_search_warrant_obtained'),
                FieldPanel('actor'),
            ]
        ),

        MultiFieldPanel(
            heading='Border Stop/Denial of Entry',
            classname='collapsible collapsed',
            children=[
                FieldPanel('border_point'),
                FieldPanel('stopped_at_border'),
                FieldPanel('target_us_citizenship_status'),
                FieldPanel('denial_of_entry'),
                FieldPanel('stopped_previously'),
                AutocompletePanel('target_nationality', 'incident.Nationality', is_single=False),
                FieldPanel('did_authorities_ask_for_device_access'),
                FieldPanel('did_authorities_ask_for_social_media_user'),
                FieldPanel('did_authorities_ask_for_social_media_pass'),
                FieldPanel('did_authorities_ask_about_work'),
                FieldPanel('were_devices_searched_or_seized'),
            ]
        ),

        MultiFieldPanel(
            heading='Physical Assault',
            classname='collapsible collapsed',
            children=[
                FieldPanel('assailant'),
                FieldPanel('was_journalist_targeted'),
            ]
        ),

        MultiFieldPanel(
            heading='Leak Prosecution (incl. Legal Case, Arrest/Detention',
            classname='collapsible collapsed',
            children=[
                AutocompletePanel('workers_whose_communications_were_obtained', 'incident.GovernmentWorker', is_single=False),
                FieldPanel('charged_under_espionage_act'),
            ]
        ),

        MultiFieldPanel(
            heading='Subpoena of Journalism (incl. Legal Case)',
            classname='collapsible collapsed',
            children=[
                FieldPanel('subpoena_type'),
                FieldPanel('subpoena_statuses'),
                FieldPanel('held_in_contempt'),
                FieldPanel('detention_status'),
            ]
        ),

        MultiFieldPanel(
            heading='Legal Order for Journalist\'s Records (incl. Legal Case)',
            classname='collapsible collapsed',
            children=[
                FieldPanel('third_party_in_possession_of_communications'),
                FieldPanel('third_party_business'),
                FieldPanel('legal_order_type'),
            ]
        ),

        MultiFieldPanel(
            heading='Prior Restraint (incl. Legal Case)',
            classname='collapsible collapsed',
            children=[
                FieldPanel('status_of_prior_restraint'),
            ]
        ),

        MultiFieldPanel(
            heading='Denial of Access',
            classname='collapsible collapsed',
            children=[
                AutocompletePanel('politicians_or_public_figures_involved', 'incident.PoliticianOrPublic', is_single=False),
            ]
        ),

        AutocompletePanel('related_incidents', 'incident.IncidentPage', is_single=False),
    ]
    settings_panels = Page.settings_panels + [
        FieldPanel('suppress_footer')
    ]

    parent_page_types = ['incident.IncidentIndexPage']

    def get_context(self, request, *args, **kwargs):
        context = super(IncidentPage, self).get_context(request, *args, **kwargs)

        related_incidents = self.get_related_incidents(threshold=4)
        context['related_incidents'] = related_incidents

        if related_incidents:
            main_category = self.get_main_category()
            if main_category:
                related_filter = {'categories': main_category.pk}
            else:
                related_filter = {}

            tags = self.tags.all()
            if tags:
                related_filter['tags'] = ','.join(str(tag.pk) for tag in tags)
            elif self.city and self.state:
                related_filter.update({'city': self.city, 'state': self.state})
            elif self.state:
                related_filter['state'] = self.state
            context['related_qs'] = urlencode(related_filter)
        return context

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

    def get_main_category(self):
        """
        Returns the first category in the list of categories
        """
        first_category = self.categories.all().first()
        if first_category:
            return first_category.category
        return None

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

        own_tags = [tag.pk for tag in self.tags.all()]
        own_tags_set = set(own_tags)

        candidates = IncidentPage.objects.annotate(
            tag_array=ExpressionWrapper(
                ArrayAgg(
                    'tags',
                    filter=models.Q(tags__isnull=False)  # excludes results of `[None]`
                ),
                output_field=ArrayField(models.IntegerField())
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
            Q(tag_array__overlap=own_tags) | Q(location_rank__gt=0)
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
        return self.teaser_image or super(IncidentPage, self).get_meta_image()

    def get_meta_description(self):
        if self.teaser:
            return self.teaser

        if self.search_description:
            return self.search_description

        return truncatewords(
            strip_tags(self.body.render_as_block()),
            20
        )
