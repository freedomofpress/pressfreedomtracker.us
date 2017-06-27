import datetime

from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
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
from incident.models import choices


class IncidentPage(Page):
    date = models.DateField()
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
    )

    body = StreamField([
        ('rich_text', blocks.RichTextBlock(icon='doc-full', label='Rich Text')),
        ('image', ImageChooserBlock()),
        ('raw_html', blocks.RawHTMLBlock()),
    ])

    teaser = RichTextField(
        help_text="This field is optional and overrides the default teaser text.",
        blank=True,
        null=True,
        max_length=384,
    )

    teaser_image = models.ForeignKey(
        'wagtailimages.image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    image_caption = RichTextField(
        max_length=255,
        blank=True,
        null=True,
    )

    image_attribution = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    targets = ClusterTaggableManager(
        through='incident.TargetsTag',
        blank=True,
        verbose_name='Targets (Journalists/Organizations)',
        related_name='targets_incidents',
    )

    tags = ClusterTaggableManager(through='common.Tag', blank=True)

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
    current_charges = ClusterTaggableManager(
        through='incident.CurrentChargesTag',
        blank=True,
        related_name='current_charge_incidents',
        verbose_name='Current Changes',
    )
    dropped_charges = ClusterTaggableManager(
        through='incident.DroppedChargesTag',
        blank=True,
        related_name='dropped_charge_incidents',
        verbose_name='Dropped Changes',
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
    jurisdiction = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name='Jurisdiction',
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
    target_nationality = ClusterTaggableManager(
        through='incident.NationalityTag',
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
    targets_whose_communications_were_obtained = ClusterTaggableManager(
        through='incident.TargetsCommunicationsObtainedTag',
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
        choices=choices.PRIOR_RESTRAINT_STAUTS,
        max_length=255,
        blank=True,
        null=True,
    )

    # Denial of Access
    politicians_or_public_figures_involved = ClusterTaggableManager(
        through='incident.PoliticiansOrPublicTag',
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
                FieldPanel('image_attribution'),
                FieldPanel('teaser'),
            ]
        ),
        MultiFieldPanel(
            heading='Details',
            children=[
                    FieldPanel('date'),
                    FieldPanel('affiliation'),
                    FieldPanel('city'),
                    AutocompletePageChooserPanel('state', page_type='incident.State'),
                    FieldPanel('targets'),
                    FieldPanel('tags'),
                    InlinePanel('categories', label='Incident categories', min_num=1),
            ]
        ),

        MultiFieldPanel(
            heading='Detention/Arrest',
            classname='collapsible collapsed',
            children=[
                FieldPanel('arrest_status'),
                FieldPanel('status_of_charges'),
                FieldPanel('current_charges'),
                FieldPanel('dropped_charges'),
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
                FieldPanel('jurisdiction'),
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
                FieldPanel('target_nationality'),
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
                FieldPanel('targets_whose_communications_were_obtained'),
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
                FieldPanel('politicians_or_public_figures_involved'),
            ]
        ),

        AutocompleteFieldPanel('related_incidents', 'incident.IncidentPage'),
    ]

    parent_page_types = ['incident.IncidentIndexPage']

    search_fields = Page.search_fields + [
        index.SearchField('body'),
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
        Returns the date this incident was last updated on.
        """
        first = self.updates.order_by('-date').first()
        if first:
            return first.date
        return self.first_published_at

    def recently_updated(self):
        """
        Determines whether an incident has been updated within the last week. Returns a boolean.
        """
        if self.last_updated():
            delta = datetime.datetime.now(datetime.timezone.utc) - self.last_updated()
            return delta.days < 7
        return False

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
