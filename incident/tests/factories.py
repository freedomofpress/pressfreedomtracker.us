import datetime
from factory import RelatedFactory, Trait, Faker, SubFactory, Sequence
import factory
import wagtail_factories

from django.utils import timezone

import incident.models
from incident.models import (
    Charge,
    IncidentAuthor,
    IncidentCategorization,
    IncidentIndexPage,
    IncidentPage,
    IncidentPageUpdates,
    IncidentPageLinks,
    Nationality,
    PoliticianOrPublic,
    EquipmentBroken,
    Equipment,
    EquipmentSeized,
    State,
    choices,
    Journalist,
    Institution,
    LawEnforcementOrganization,
    TargetedJournalist,
    GovernmentWorker,
    TopicPage,
    Venue,
)
from common.tests.factories import (
    CustomImageFactory,
    CategoryPageFactory,
    CommonTagFactory,
    PersonPageFactory,
    RichTextTemplateBlockFactory,
    AlignedCaptionedImageBlockFactory,
    RawHTMLBlockFactory,
    TweetEmbedBlockFactory,
    RichTextBlockQuoteBlockFactory,
    PullQuoteBlockFactory,
    AlignedCaptionedEmbedBlockFactory,
)
from common.tests.utils import StreamfieldProvider
from menus.factories import MainMenuItemFactory


Faker.add_provider(StreamfieldProvider)


class IncidentIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = IncidentIndexPage

    class Params:
        main_menu = Trait(
            menu=RelatedFactory(MainMenuItemFactory, 'link_page', for_page=True)
        )


class EquipmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Equipment
    name = factory.Sequence(lambda n: f'Equipment {n}')


class EquipmentSeizedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EquipmentSeized
    equipment = SubFactory(EquipmentFactory)
    quantity = 1


class EquipmentBrokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EquipmentBroken
    equipment = SubFactory(EquipmentFactory)
    quantity = 1


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    class Params:
        unique_title = factory.Trait(
            title=factory.Sequence(
                lambda n: 'Title {n}'.format(n=n)
            )
        )


class VenueFactory(ItemFactory):
    class Meta:
        model = Venue

    title = factory.Sequence(lambda n: f'Venue {n}')


class LawEnforcementOrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LawEnforcementOrganization

    title = factory.Sequence(lambda n: f'Law Enforcement Organization {n}')


class IncidentUpdateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IncidentPageUpdates

    title = factory.Sequence(lambda n: f'Update {n}')
    date = factory.LazyFunction(timezone.now)
    body = None


class IncidentUpdateWithBodyFactory(IncidentUpdateFactory):
    body = wagtail_factories.StreamFieldFactory({
        'rich_text': factory.SubFactory(RichTextTemplateBlockFactory),
        'image': factory.SubFactory(
            wagtail_factories.blocks.ImageChooserBlockFactory
        ),
        'raw_html': factory.SubFactory(RawHTMLBlockFactory),
        'tweet': factory.SubFactory(TweetEmbedBlockFactory),
        'blockquote': factory.SubFactory(RichTextBlockQuoteBlockFactory),
        'video': factory.SubFactory(AlignedCaptionedEmbedBlockFactory),
    })


class IncidentLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IncidentPageLinks

    sort_order = Sequence(int)
    title = 'Link'
    url = 'https://freedom.press'
    publication = None


class StateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = State
        django_get_or_create = ('name', )
    name = factory.Sequence(lambda n: f'State {n}')
    abbreviation = factory.Sequence(lambda n: f'{n}')


class IncidentPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = IncidentPage
        exclude = ('teaser_image_text', 'image_caption_text')

    first_published_at = factory.LazyFunction(timezone.now)
    last_published_at = factory.LazyAttribute(
        lambda o: o.first_published_at + datetime.timedelta(days=3)
    )
    latest_revision_created_at = factory.LazyAttribute(
        lambda o: o.first_published_at + datetime.timedelta(days=5)
    )

    title = factory.Sequence(lambda n: f'Incident {n}')
    date = factory.LazyFunction(datetime.date.today)
    city = None
    state = factory.SubFactory(StateFactory)
    longitude = None
    latitude = None
    body = None
    introduction = None
    teaser = None
    teaser_image = None
    image_caption = None

    # Detention/arrest
    arrest_status = None
    status_of_charges = None
    arresting_authority = None
    release_date = None
    detention_date = None
    unnecessary_use_of_force = False

    # Equipment seizure or damage
    status_of_seized_equipment = None
    is_search_warrant_obtained = False
    actor = None

    # Border stop
    border_point = None
    target_us_citizenship_status = None
    denial_of_entry = False
    stopped_previously = False
    did_authorities_ask_for_device_access = None
    did_authorities_ask_about_work = None

    # Physical assault
    assailant = None
    was_journalist_targeted = None

    # Leak prosecution
    charged_under_espionage_act = False

    # Subpoena of journalism
    subpoena_type = None
    subpoena_statuses = None
    held_in_contempt = None
    detention_status = None

    # Legal case
    case_number = None
    case_type = None
    case_statuses = []

    class Params:
        arrest = factory.Trait(
            arrest_status=factory.Iterator(
                choices.ARREST_STATUS, getter=lambda c: c[0]),
            status_of_charges=factory.Iterator(
                choices.STATUS_OF_CHARGES, getter=lambda c: c[0]),
            arresting_authority=SubFactory(LawEnforcementOrganizationFactory),
            release_date=datetime.date.today(),
            detention_date=datetime.date.today() - datetime.timedelta(days=3),
            unnecessary_use_of_force=False
        )
        equipment_search = factory.Trait(
            status_of_seized_equipment=factory.Iterator(
                choices.STATUS_OF_SEIZED_EQUIPMENT, getter=lambda c: c[0]),
            is_search_warrant_obtained=False,
            actor=factory.Iterator(choices.ACTORS, getter=lambda c: c[0]),
            equip_search=RelatedFactory(EquipmentSeizedFactory, 'incident'),
        )
        border_stop = factory.Trait(
            border_point='City A',
            target_us_citizenship_status=factory.Iterator(
                choices.CITIZENSHIP_STATUS_CHOICES, getter=lambda c: c[0]),
            denial_of_entry=False,
            stopped_previously=False,
            # did_authorities_ask_for_device_access=factory.Iterator(
            #     choices.MAYBE_BOOLEAN, getter=lambda c: c[0]),
            did_authorities_ask_for_device_access=factory.Iterator(
                choices.MAYBE_BOOLEAN, getter=lambda c: c[0]
            ),
            did_authorities_ask_about_work=factory.Iterator(
                choices.MAYBE_BOOLEAN, getter=lambda c: c[0]
            ),
        )
        assault = factory.Trait(
            assailant=factory.Iterator(choices.ACTORS, getter=lambda c: c[0]),
            was_journalist_targeted=factory.Iterator(
                choices.MAYBE_BOOLEAN, getter=lambda c: c[0]
            ),
        )
        leak_case = factory.Trait(
            # workers_whose_communications_were_obtained=2,
            charged_under_espionage_act=False,
        )
        subpoena = factory.Trait(
            legal_order_target=choices.LegalOrderTarget.JOURNALIST,
            subpoena_type=factory.Iterator(
                choices.SUBPOENA_TYPE, getter=lambda c: c[0]),
            # subpoena_statuses=factory.Iterator(
            #     choices.SUBPOENA_STATUS, getter=lambda c: c[0]
            # ),
            subpoena_statuses=factory.List(
                [factory.Iterator(
                    choices.SUBPOENA_STATUS, getter=lambda c: c[0])]
                # factory.LazyFunction(lambda: random_choice_list(choices.SUBPOENA_SUBJECT))
            ),
            held_in_contempt=factory.Iterator(
                choices.MAYBE_BOOLEAN, getter=lambda c: c[0]
            ),
            detention_status=factory.Iterator(
                choices.DETENTION_STATUS, getter=lambda c: c[0]),
            name_of_business='Megacorp Industries',
            third_party_business=factory.Iterator(
                choices.THIRD_PARTY_BUSINESS, getter=lambda c: c[0]),
            legal_order_type=factory.Iterator(
                choices.LEGAL_ORDER_TYPE, getter=lambda c: c[0]),
            legal_order_venue=choices.LegalOrderVenue.STATE,
        )
        prior_restraint = factory.Trait(
            status_of_prior_restraint=factory.Iterator(
                choices.STATUS_OF_PRIOR_RESTRAINT, getter=lambda c: c[0]),
            mistakenly_released_materials=False,
        )
        denial_of_access = factory.Trait(
            politicians_or_public_figures_involved=1,
            type_of_denial=[choices.TypeOfDenial.OTHER],
        )
        equipment_damage = Trait(
            equip_damage=RelatedFactory(EquipmentBrokenFactory, 'incident'),
        )
        chilling_statement = Trait()
        other_incident = Trait()

    # https://adamj.eu/tech/2014/09/03/factory-boy-fun/
    @factory.post_generation
    def institution_targets(self, create, count):
        if count is None:
            count = 2
        make_target = getattr(InstitutionFactory, 'create' if create else 'build')
        targets = []
        for i in range(count):
            t = make_target()
            self.targeted_institutions.add(t)
            targets.append(t)
        if not create:
            self._prefetched_objects_cache = {'targeted_institutions': targets}

    @factory.post_generation
    def journalist_targets(self, create, count, **kwargs):
        if count is None:
            count = 0
        make_targeted_journalist = getattr(TargetedJournalistFactory, 'create' if create else 'build')
        targets = []
        for i in range(count):
            make_targeted_journalist(incident=self, **kwargs)
        if not create:
            self._prefetched_objects_cache = {'targeted_institutions': targets}

    @factory.post_generation
    def workers_whose_communications_were_obtained(self, create, count):
        if count is None:
            return
        make_worker = getattr(GovernmentWorkerFactory, 'create' if create else 'build')
        workers = []
        for i in range(count):
            w = make_worker()
            w.incidents.add(self)
            workers.append(w)
        if not create:
            self._prefetched_objects_cache = {
                'workers_whose_communications_were_obtained': workers
            }

    @factory.post_generation
    def current_charges(self, create, count):
        if count is None:
            return
        make_charge = getattr(ChargeFactory, 'create' if create else 'build')
        charges = []
        for i in range(count):
            t = make_charge()
            t.current_charge_incidents.add(self)
            charges.append(t)
        if not create:
            self._prefetched_objects_cache = {'current_charges': charges}

    @factory.post_generation
    def dropped_charges(self, create, count):
        if count is None:
            return
        make_charge = getattr(ChargeFactory, 'create' if create else 'build')
        charges = []
        for i in range(count):
            t = make_charge()
            t.dropped_charge_incidents.add(self)
            charges.append(t)
        if not create:
            self._prefetched_objects_cache = {'dropped_charges': charges}

    @factory.post_generation
    def target_nationality(self, create, count):
        if count is None:
            return
        make_nat = getattr(NationalityFactory, 'create' if create else 'build')
        nats = []
        for i in range(count):
            t = make_nat()
            t.nationality_incidents.add(self)
            nats.append(t)
        if not create:
            self._prefetched_objects_cache = {'target_nationality': nats}

    @factory.post_generation
    def politicians_or_public_figures_involved(self, create, count):
        if count is None:
            return
        make_pol = getattr(PoliticianOrPublicFactory,
                           'create' if create else 'build')
        pols = []
        for i in range(count):
            t = make_pol()
            t.politicians_or_public_incidents.add(self)
            pols.append(t)
        if not create:
            self._prefetched_objects_cache = {
                'politicians_or_public_figures_involved': pols
            }

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for author in extracted:
                IncidentAuthorFactory(
                    parent_page=self,
                    author=author,
                )

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for category in extracted:
                IncidentCategorizationFactory(
                    incident_page=self,
                    category=category,
                )

    @factory.post_generation
    def related_incidents(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.related_incidents.set(extracted)


class IncidentPageWithBodyFactory(IncidentPageFactory):
    teaser_image = factory.SubFactory(CustomImageFactory)
    body = wagtail_factories.StreamFieldFactory({
        'rich_text': factory.SubFactory(RichTextTemplateBlockFactory),
        'image': factory.SubFactory(
            wagtail_factories.blocks.ImageChooserBlockFactory
        ),
        'aligned_image': factory.SubFactory(AlignedCaptionedImageBlockFactory),
        'raw_html': factory.SubFactory(RawHTMLBlockFactory),
        'tweet': factory.SubFactory(TweetEmbedBlockFactory),
        'blockquote': factory.SubFactory(RichTextBlockQuoteBlockFactory),
        'pull_quote': factory.SubFactory(PullQuoteBlockFactory),
        'video': factory.SubFactory(AlignedCaptionedEmbedBlockFactory),
    })


class InexactDateIncidentPageFactory(IncidentPageFactory):
    exact_date_unknown = True
    date = datetime.date(2017, 3, 1)


class IncidentCategorizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IncidentCategorization
    sort_order = factory.Sequence(lambda n: n)
    incident_page = factory.SubFactory(IncidentPageFactory)
    category = factory.SubFactory(CategoryPageFactory)


class IncidentAuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IncidentAuthor
    sort_order = factory.Sequence(lambda n: n)
    parent_page = factory.SubFactory(IncidentPageFactory)
    author = factory.SubFactory(PersonPageFactory)


class TopicPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = TopicPage

    title = factory.Sequence(lambda n: 'Category {n}'.format(n=n))
    incident_tag = factory.SubFactory(CommonTagFactory)


class SnippetFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    class Params:
        unique_name = factory.Trait(
            name=factory.Sequence(
                lambda n: 'Name {n}'.format(n=n)
            )
        )


class GovernmentWorkerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GovernmentWorker

    title = factory.Sequence(lambda n: f'Worker {n}')


class ChargeFactory(ItemFactory):
    class Meta:
        model = Charge
    title = factory.Sequence(lambda n: f'Charge {n}')


class ChargeUpdateFactory(ItemFactory):
    class Meta:
        model = incident.models.ChargeUpdate

    date = factory.LazyFunction(timezone.now)
    status = choices.STATUS_OF_CHARGES[0][0]


class IncidentChargeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = incident.models.IncidentCharge

    incident_page = factory.SubFactory(IncidentPageFactory)
    charge = factory.SubFactory(ChargeFactory)
    date = factory.LazyFunction(timezone.now)
    status = choices.STATUS_OF_CHARGES[0][0]


class IncidentChargeWithUpdatesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = incident.models.IncidentCharge

    incident_page = factory.SubFactory(IncidentPageFactory)
    charge = factory.SubFactory(ChargeFactory)
    date = factory.LazyFunction(timezone.now)
    status = choices.STATUS_OF_CHARGES[0][0]
    update1 = factory.RelatedFactory(
        ChargeUpdateFactory,
        factory_related_name='incident_charge',
    )
    update2 = factory.RelatedFactory(
        ChargeUpdateFactory,
        factory_related_name='incident_charge',
    )
    update3 = factory.RelatedFactory(
        ChargeUpdateFactory,
        factory_related_name='incident_charge',
    )


class LegalOrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = incident.models.LegalOrder

    incident_page = factory.SubFactory(IncidentPageFactory)
    order_type = choices.LegalOrderType.SUBPOENA
    information_requested = choices.InformationRequested.OTHER
    status = choices.LegalOrderStatus.PENDING
    date = factory.LazyFunction(timezone.now)


class LegalOrderUpdateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = incident.models.LegalOrderUpdate

    date = factory.LazyFunction(timezone.now)
    status = choices.LegalOrderStatus.UNKNOWN


class LegalOrderWithUpdatesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = incident.models.LegalOrder

    incident_page = factory.SubFactory(IncidentPageFactory)
    order_type = choices.LegalOrderType.SUBPOENA
    information_requested = choices.LegalOrderType.OTHER
    status = choices.LegalOrderStatus.PENDING
    date = factory.LazyFunction(timezone.now)
    update1 = factory.RelatedFactory(
        LegalOrderUpdateFactory,
        factory_related_name='legal_order',
        date=factory.LazyAttribute(lambda o: o.factory_parent.date + datetime.timedelta(days=1)),
        sort_order=1,
    )
    update2 = factory.RelatedFactory(
        LegalOrderUpdateFactory,
        factory_related_name='legal_order',
        date=factory.LazyAttribute(lambda o: o.factory_parent.date + datetime.timedelta(days=2)),
        sort_order=2,
    )
    update3 = factory.RelatedFactory(
        LegalOrderUpdateFactory,
        factory_related_name='legal_order',
        date=factory.LazyAttribute(lambda o: o.factory_parent.date + datetime.timedelta(days=3)),
        sort_order=3,
    )


class NationalityFactory(ItemFactory):
    class Meta:
        model = Nationality
    title = factory.Sequence(lambda n: f'Nationality {n}')


class PoliticianOrPublicFactory(ItemFactory):
    class Meta:
        model = PoliticianOrPublic
    title = factory.Sequence(lambda n: f'Politician {n}')


class JournalistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Journalist

    title = factory.Sequence(lambda n: f'Journalist {n}')


class InstitutionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Institution

    title = factory.Sequence(lambda n: f'Institution {n}')


class TargetedJournalistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TargetedJournalist

    journalist = factory.SubFactory(JournalistFactory)
    incident = factory.SubFactory(IncidentPageFactory)
    institution = factory.SubFactory(InstitutionFactory)
