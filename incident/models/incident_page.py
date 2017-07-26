import datetime

from django.db import models
from modelcluster.fields import ParentalManyToManyField
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField, RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index

from autocomplete.edit_handlers import AutocompleteFieldPanel, AutocompletePageChooserPanel
from common.blocks import RichTextBlockQuoteBlock, AlignedCaptionedEmbedBlock
from incident.models import choices
from incident.circuits import CIRCUITS_BY_STATE
from statistics.blocks import StatisticsBlock


class IncidentPage(Page):
    date = models.DateField()

    exact_date_unknown = models.BooleanField(
        default=False,
        help_text='If checked, only the month and year of the incident will be displayed. The date above will be used in filtering by date.'
    )

    affiliation = models.CharField(
        max_length=255,
        default='Independent',
        blank=True,
        null=True,
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
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
        ('blockquote', RichTextBlockQuoteBlock()),
        ('video', AlignedCaptionedEmbedBlock()),
        ('statistics', StatisticsBlock()),
    ])

    teaser = RichTextField(
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

    image_caption = RichTextField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Image description displayed below the image. Organization/Photographer can be set via the image attribution.'
    )

    targets = ParentalManyToManyField(
        'incident.Target',
        blank=True,
        verbose_name='Targets (Journalists/Organizations)',
        related_name='targets_incidents',
    )

    tags = ParentalManyToManyField(
        'common.CommonTag',
        blank=True,
        verbose_name='Tags',
        related_name='tagged_items',
    )

    related_incidents = ParentalManyToManyField('self', blank=True)

    # Detention/Arrest
    arrest_status = models.CharField(
        choices=choices.ARREST_STATUS,
        max_length=255,
        null=True,
        blank=True,
    )
    status_of_charges = models.CharField(
        choices=choices.STATUS_OF_CHARGES,
        max_length=255,
        null=True,
        blank=True,
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
    release_date = models.DateField(blank=True, null=True)
    detention_date = models.DateField(
        blank=True,
        null=True,
        help_text='This field will default to the date field if not specified.',
    )
    unnecessary_use_of_force = models.BooleanField(default=False)

    # Legal Case
    lawsuit_name = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
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
    )
    is_search_warrant_obtained = models.BooleanField(default=False)
    actor = models.CharField(
        choices=choices.ACTORS,
        max_length=255,
        null=True,
        blank=True,
    )

    # Border Stop/Denial of Entry
    border_point = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )
    stopped_at_border = models.BooleanField(default=False)
    target_us_citizenship_status = models.CharField(
        choices=choices.CITIZENSHIP_STATUS_CHOICES,
        max_length=255,
        blank=True,
        null=True,
    )
    denial_of_entry = models.BooleanField(default=False)
    stopped_previously = models.BooleanField(default=False)
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
    )
    did_authorities_ask_for_social_media_user = models.CharField(
        choices=choices.MAYBE_BOOLEAN,
        max_length=255,
        blank=True,
        null=True,
    )
    did_authorities_ask_for_social_media_pass = models.CharField(
        choices=choices.MAYBE_BOOLEAN,
        max_length=255,
        blank=True,
        null=True,
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
    )

    # Physical Assault
    assailant = models.CharField(
        choices=choices.ACTORS,
        max_length=255,
        blank=True,
        null=True,
    )
    was_journalist_targeted = models.CharField(
        choices=choices.MAYBE_BOOLEAN,
        max_length=255,
        blank=True,
        null=True,
    )

    # Leak Prosecution
    targets_whose_communications_were_obtained = ParentalManyToManyField(
        'incident.Target',
        blank=True,
        verbose_name='Journalists/Organizations whose communications were obtained in leak investigation',
        related_name='targets_communications_obtained_incidents',
    )
    charged_under_espionage_act = models.BooleanField(default=False)

    # Subpoena of Journalism
    subpoena_type = models.CharField(
        choices=choices.SUBPOENA_TYPE,
        max_length=255,
        blank=True,
        null=True,
    )
    subpoena_status = models.CharField(
        choices=choices.SUBPOENA_STATUS,
        max_length=255,
        blank=True,
        null=True,
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
    )

    # Legal Order for Journalist's Records
    third_party_in_possession_of_communications = models.CharField(
        max_length=512,
        blank=True,
        null=True,
    )
    third_party_business = models.CharField(
        choices=choices.THIRD_PARTY_BUSINESS,
        max_length=255,
        blank=True,
        null=True,
    )
    legal_order_type = models.CharField(
        choices=choices.LEGAL_ORDER_TYPES,
        max_length=255,
        blank=True,
        null=True,
    )

    # Prior Restraint
    status_of_prior_restraint = models.CharField(
        choices=choices.PRIOR_RESTRAINT_STATUS,
        max_length=255,
        blank=True,
        null=True,
    )

    # Denial of Access
    politicians_or_public_figures_involved = ParentalManyToManyField(
        'incident.PoliticianOrPublic',
        blank=True,
        related_name='politicians_or_public_incidents',
        verbose_name='Politicians or public officials involved',
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        InlinePanel('updates', label='Updates'),
        InlinePanel(
            'links',
            label='Sources',
            help_text="Links to resources and news articles related to this"
                      "incident. Displayed as footnotes."
        ),

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
                    FieldPanel('affiliation'),
                    FieldPanel('city'),
                    AutocompletePageChooserPanel('state', page_type='incident.State'),
                    AutocompleteFieldPanel('targets', 'incident.Target'),
                    AutocompleteFieldPanel('tags', 'common.CommonTag'),
                    InlinePanel('categories', label='Incident categories', min_num=1),
            ]
        ),

        MultiFieldPanel(
            heading='Detention/Arrest',
            classname='collapsible collapsed',
            children=[
                FieldPanel('arrest_status'),
                FieldPanel('status_of_charges'),
                AutocompleteFieldPanel('current_charges', 'incident.Charge'),
                AutocompleteFieldPanel('dropped_charges', 'incident.Charge'),
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
                AutocompleteFieldPanel('venue', 'incident.Venue'),
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
                AutocompleteFieldPanel('target_nationality', 'incident.Nationality'),
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
                AutocompleteFieldPanel('targets_whose_communications_were_obtained', 'incident.Target'),
                FieldPanel('charged_under_espionage_act'),
            ]
        ),

        MultiFieldPanel(
            heading='Subpoena of Journalism (incl. Legal Case)',
            classname='collapsible collapsed',
            children=[
                FieldPanel('subpoena_type'),
                FieldPanel('subpoena_status'),
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
                AutocompleteFieldPanel('politicians_or_public_figures_involved', 'incident.PoliticianOrPublic'),
            ]
        ),

        AutocompleteFieldPanel('related_incidents', 'incident.IncidentPage'),
    ]

    parent_page_types = ['incident.IncidentIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.FilterField('date'),
        index.FilterField('category_id'),
        index.FilterField('fuzzy_date'),
    ]

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

    def get_main_category(self):
        """
        Returns the first category in the list of categories
        """
        return self.categories.all().first().category

    def get_related_incidents(self):
        """
        Returns related incidents and/or other incidents in the same category.
        """

        # If there are one or fewer related incidents, we will append more incidents from the same category, up to a maximum number
        related_to_incident_qs = self.related_incidents.all()
        related_incidents = list(related_to_incident_qs)
        main_category = self.get_main_category()

        # Maximum of related incidents to return, minimum of 2
        maximum = max(2, min(4, len(related_incidents)))

        if len(related_incidents) >= 2:
            return related_incidents[:maximum]

        # only add up to two more incidents from the main category
        maximum += maximum % 2

        related_incidents += list(
            IncidentPage.objects.filter(
                live=True,
                categories__category=main_category
            ).exclude(
                id=self.id
            ).difference(
                related_to_incident_qs
            )[:(maximum - len(related_incidents))]
        )

        return related_incidents

    def get_court_circuit(self):
        if self.state:
            for state, circuit in CIRCUITS_BY_STATE.items():
                if state == self.state.name:
                    return circuit
        return None
