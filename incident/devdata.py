import datetime
from factory import RelatedFactory, Trait, Faker, SubFactory, LazyAttribute, Iterator, Sequence
import factory
import random
import wagtail_factories
from wagtail.core.rich_text import RichText

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
)
from common.models import CustomImage
from common.tests.factories import (
    CategoryPageFactory,
    CommonTagFactory,
    PersonPageFactory,
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
        django_get_or_create = ('name',)
    name = Faker('word', ext_word_list=['abacus', 'calculator', 'ruler', 'compass', 'graph paper', 'protractor', 'planimeter', 'multimeter', 'photometer', 'diffuser', 'hygrometer', 'timer', 'microscope'])


class EquipmentSeizedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EquipmentSeized
    equipment = SubFactory(EquipmentFactory)
    quantity = LazyAttribute(lambda _: random.randint(1, 5))


class EquipmentBrokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EquipmentBroken
    equipment = SubFactory(EquipmentFactory)
    quantity = LazyAttribute(lambda _: random.randint(1, 5))


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    class Params:
        unique_title = factory.Trait(
            title=factory.Sequence(
                lambda n: 'Title {n}'.format(n=n)
            )
        )


class LawEnforcementOrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LawEnforcementOrganization
        django_get_or_create = ('title',)
    title = factory.Faker('sentence', nb_words=3)


class IncidentUpdateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IncidentPageUpdates

    title = Faker('sentence')
    date = Faker('past_datetime', start_date='-15d', tzinfo=datetime.timezone.utc)
    body = Faker('streamfield', fields=['rich_text_paragraph', 'raw_html'])


class MultimediaIncidentUpdateFactory(IncidentUpdateFactory):
    body = Faker('streamfield', fields=['rich_text_paragraph', 'bare_image', 'raw_html', 'blockquote'])


class IncidentLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = IncidentPageLinks

    sort_order = Sequence(int)
    title = Faker('sentence')
    url = Faker('url', schemes=['https'])
    publication = Faker('company')


class SnippetFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    class Params:
        unique_name = factory.Trait(
            name=factory.Sequence(
                lambda n: 'Name {n}'.format(n=n)
            )
        )


class StateFactory(SnippetFactory):
    class Meta:
        model = State
        django_get_or_create = ('name',)
    name = factory.Faker('state')


def random_choice(choices):
    return random.choice([x[0] for x in choices])


def random_choice_list(choices):
    return random.sample([x[0] for x in choices], k=random.randint(0, len(choices)))


class IncidentPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = IncidentPage
        exclude = ('image_caption_text', 'title_text')

    first_published_at = Faker(
        'past_datetime',
        start_date='-90d',
        tzinfo=datetime.timezone.utc,
    )
    last_published_at = factory.LazyAttribute(
        lambda o: o.first_published_at + datetime.timedelta(days=3)
    )
    latest_revision_created_at = factory.LazyAttribute(
        lambda o: o.first_published_at + datetime.timedelta(days=5)
    )

    image_caption_text = Faker('sentence')
    title_text = Faker('sentence')
    title = factory.LazyAttribute(lambda o: o.title_text.rstrip('.'))

    date = factory.Faker('date_between', start_date='-1y', end_date='-30d')
    city = factory.Faker('city')
    state = factory.SubFactory(StateFactory)
    longitude = factory.Faker('longitude')
    latitude = factory.Faker('latitude')
    body = Faker('streamfield', fields=['rich_text_paragraph', 'raw_html'])
    teaser = factory.Faker('sentence')
    teaser_image = None
    image_caption = factory.LazyAttribute(lambda o: RichText(o.image_caption_text))

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
    stopped_at_border = False
    target_us_citizenship_status = None
    denial_of_entry = False
    stopped_previously = False
    did_authorities_ask_for_device_access = None
    did_authorities_ask_for_social_media_pass = None
    did_authorities_ask_for_social_media_user = None
    did_authorities_ask_about_work = None
    were_devices_searched_or_seized = None

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
    case_number = factory.Faker('pystr_format', string_format='{{name}} v. {{name}}')
    case_statuses = factory.LazyFunction(lambda: random_choice_list(choices.CASE_STATUS))

    class Params:
        arrest = factory.Trait(
            arrest_status=factory.Iterator(
                choices.ARREST_STATUS, getter=lambda c: c[0]),
            status_of_charges=factory.Iterator(
                choices.STATUS_OF_CHARGES, getter=lambda c: c[0]),
            arresting_authority=SubFactory(LawEnforcementOrganizationFactory),
            release_date=datetime.date.today(),
            detention_date=datetime.date.today() - datetime.timedelta(days=3),
            unnecessary_use_of_force=factory.Faker('boolean'),
        )
        equipment_search = factory.Trait(
            status_of_seized_equipment=factory.Iterator(
                choices.STATUS_OF_SEIZED_EQUIPMENT, getter=lambda c: c[0]),
            is_search_warrant_obtained=factory.Faker('boolean'),
            actor=factory.Iterator(choices.ACTORS, getter=lambda c: c[0]),
            equip_search=RelatedFactory(EquipmentSeizedFactory, 'incident'),
        )
        border_stop = factory.Trait(
            border_point=factory.Faker('city'),
            stopped_at_border=factory.Faker('boolean'),
            target_us_citizenship_status=factory.Iterator(
                choices.CITIZENSHIP_STATUS_CHOICES, getter=lambda c: c[0]),
            denial_of_entry=factory.Faker('boolean'),
            stopped_previously=factory.Faker('boolean'),
            # did_authorities_ask_for_device_access=factory.Iterator(
            #     choices.MAYBE_BOOLEAN, getter=lambda c: c[0]),
            did_authorities_ask_for_device_access=factory.LazyFunction(lambda: random_choice(choices.MAYBE_BOOLEAN)),
            did_authorities_ask_for_social_media_user=factory.LazyFunction(lambda: random_choice(choices.MAYBE_BOOLEAN)),
            did_authorities_ask_for_social_media_pass=factory.LazyFunction(lambda: random_choice(choices.MAYBE_BOOLEAN)),
            did_authorities_ask_about_work=factory.LazyFunction(lambda: random_choice(choices.MAYBE_BOOLEAN)),
            were_devices_searched_or_seized=factory.LazyFunction(lambda: random_choice(choices.MAYBE_BOOLEAN)),
        )
        physical_attack = factory.Trait(
            assailant=factory.Iterator(choices.ACTORS, getter=lambda c: c[0]),
            was_journalist_targeted=factory.LazyFunction(
                lambda: random_choice(choices.MAYBE_BOOLEAN)
            ),
        )
        leak_case = factory.Trait(
            # workers_whose_communications_were_obtained=2,
            charged_under_espionage_act=factory.Faker('boolean'),
        )
        subpoena = factory.Trait(
            subpoena_type=factory.Iterator(
                choices.SUBPOENA_TYPE, getter=lambda c: c[0]),
            subpoena_statuses=factory.LazyFunction(lambda: random_choice_list(choices.SUBPOENA_STATUS)),
            # subpoena_statuses=factory.List(
            #     # [factory.Iterator(
            #     #     choices.SUBPOENA_STATUS, getter=lambda c: c[0])]
            #     factory.LazyFunction(lambda: random_choice_list(choices.SUBPOENA_SUBJECT))
            # ),
            held_in_contempt=factory.LazyFunction(lambda: random_choice(choices.MAYBE_BOOLEAN)),
            detention_status=factory.Iterator(
                choices.DETENTION_STATUS, getter=lambda c: c[0]),
            third_party_in_possession_of_communications=factory.Faker('company'),
            third_party_business=factory.Iterator(
                choices.THIRD_PARTY_BUSINESS, getter=lambda c: c[0]),
            legal_order_type=factory.Iterator(
                choices.LEGAL_ORDER_TYPE, getter=lambda c: c[0]),
        )
        prior_restraint = factory.Trait(
            status_of_prior_restraint=factory.Iterator(
                choices.STATUS_OF_PRIOR_RESTRAINT, getter=lambda c: c[0]),
        )
        denial_of_access = factory.Trait(
            politicians_or_public_figures_involved=random.randint(1, 4),
        )
        equipment_damage = Trait(
            equip_damage=RelatedFactory(EquipmentBrokenFactory, 'incident'),
        )
        chilling_statement = Trait()
        other_incident = Trait()

    @factory.post_generation
    def tags(self, create, argument, **kwargs):
        if not argument or not isinstance(argument, int):
            count = 0
        else:
            count = argument

        make_tag = getattr(CommonTagFactory, 'create' if create else 'build')
        tags = []
        for i in range(count):
            tag = make_tag(**kwargs)
            self.tags.add(tag)
            tags.append(tag)
        if not create:
            self._prefetched_object_cache = {'tags': tags }

    # https://adamj.eu/tech/2014/09/03/factory-boy-fun/
    @factory.post_generation
    def institution_targets(self, create, count):
        if not create:
            # Simple build, do nothing.
            return
        if count is None:
            count = 2
        make_target = getattr(InstitutionFactory, 'create' if create else 'build')
        targets = []
        for i in range(count):
            t = make_target()
            self.targeted_institutions.add(t)
            targets.append(t)

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


class MultimediaIncidentPageFactory(IncidentPageFactory):
    body = Faker('streamfield', fields=['rich_text', 'bare_image', 'blockquote', 'raw_html'])
    teaser_image = Iterator(
        CustomImage.objects.filter(collection__name='Photos')
    )


class InexactDateIncidentPageFactory(IncidentPageFactory):
    exact_date_unknown = True
    date = factory.Faker(
        'date_between',
        start_date=datetime.date(2017, 3, 1),
        end_date=datetime.date(2017, 3, 31),
    )


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
        django_get_or_create = ('title',)
        exclude = ('first_name', 'last_name')

    title = factory.LazyAttribute(
        lambda o: '{0} {1}. Worker'.format(o.first_name, o.last_name[0])
    )

    # Lazy values
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class ChargeFactory(ItemFactory):
    class Meta:
        model = Charge
        django_get_or_create = ('title',)
    title = factory.Faker('sentence', nb_words=3)


class NationalityFactory(ItemFactory):
    class Meta:
        model = Nationality
        django_get_or_create = ('title',)
    title = factory.Faker('country')


class PoliticianOrPublicFactory(ItemFactory):
    class Meta:
        model = PoliticianOrPublic
        django_get_or_create = ('title',)
    title = factory.Faker('name')


class StateFactory(SnippetFactory):
    class Meta:
        model = State
        django_get_or_create = ('name',)
    name = factory.Faker('state')


class JournalistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Journalist
        django_get_or_create = ('title',)

    title = factory.Faker('name')


class InstitutionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Institution
        django_get_or_create = ('title',)
        exclude = ('city',)

    title = factory.LazyAttributeSequence(
        lambda o, n: 'The {city} {paper} {n}'.format(
            city=o.city,
            paper=random.choice(['Tribune', 'Herald', 'Sun', 'Daily News', 'Post']),
            n=n,
        )
    )

    # Lazy values
    city = factory.Faker('city')


class TargetedJournalistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TargetedJournalist

    journalist = factory.SubFactory(JournalistFactory)
    incident = factory.SubFactory(IncidentPageFactory)
    institution = factory.SubFactory(InstitutionFactory)
