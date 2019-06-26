import datetime
from factory import RelatedFactory, Trait, Faker, SubFactory, LazyAttribute, Iterator
import factory
import random
import wagtail_factories
from wagtail.core.rich_text import RichText

from incident.models import (
    Charge,
    IncidentCategorization,
    IncidentIndexPage,
    IncidentPage,
    Nationality,
    PoliticianOrPublic,
    EquipmentBroken,
    Equipment,
    EquipmentSeized,
    Target,
    State,
    choices,
)
from common.models import CustomImage
from common.tests.factories import CategoryPageFactory, RichTextBlockFactory


class IncidentIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = IncidentIndexPage

    class Params:
        main_menu = Trait(
            menu=RelatedFactory(MainMenuItemFactory, 'link_page', for_page=True)
        )


class EquipmentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Equipment
        django_get_or_create = ('name',)
    name = Faker('word', ext_word_list=['abacus', 'calculator', 'ruler', 'compass', 'graph paper', 'protractor', 'planimeter', 'multimeter', 'photometer', 'diffuser', 'hygrometer', 'timer', 'microscope'])


class EquipmentSeizedFactory(factory.DjangoModelFactory):
    class Meta:
        model = EquipmentSeized
    equipment = SubFactory(EquipmentFactory)
    quantity = LazyAttribute(lambda _: random.randint(1, 5))


class EquipmentBrokenFactory(factory.DjangoModelFactory):
    class Meta:
        model = EquipmentBroken
    equipment = SubFactory(EquipmentFactory)
    quantity = LazyAttribute(lambda _: random.randint(1, 5))


class IncidentPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = IncidentPage
        exclude = ('teaser_image_text', 'image_caption_text')

    image_caption_text = Faker('sentence')
    teaser_image_text = Faker('sentence')
    title = factory.Faker('sentence')
    date = factory.Faker('date')
    city = factory.Faker('city')
    body = wagtail_factories.StreamFieldFactory({
        'rich_text': RichTextBlockFactory,
        'image': wagtail_factories.ImageChooserBlockFactory,
        'raw_html': wagtail_factories.CharBlockFactory,
    })
    affiliation = factory.Faker('word')
    teaser = factory.LazyAttribute(lambda o: RichText(o.teaser_image_text))
    teaser_image = Iterator(
        CustomImage.objects.filter(collection__name='Banners')
    )  # for use with the createincidents command
    image_caption = factory.LazyAttribute(lambda o: RichText(o.image_caption_text))

    # Detention/arrest
    arrest_status = None
    status_of_charges = None
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
    subpoena_status = None
    held_in_contempt = None
    detention_status = None

    class Params:
        arrest = factory.Trait(
            arrest_status=factory.Iterator(
                choices.ARREST_STATUS, getter=lambda c: c[0]),
            status_of_charges=factory.Iterator(
                choices.STATUS_OF_CHARGES, getter=lambda c: c[0]),
            current_charges=2,
            dropped_charges=2,
            release_date=datetime.date.today(),
            detention_date=datetime.date.today() - datetime.timedelta(days=3),
            unnecessary_use_of_force=factory.Faker('boolean'),
        )
        equipment_search= factory.Trait(
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
            target_nationality=1, #TODO: make into factory
            did_authorities_ask_for_device_access=factory.Iterator(
                choices.MAYBE_BOOLEAN, getter=lambda c: c[0]),
            did_authorities_ask_for_social_media_user=factory.Iterator(
                choices.MAYBE_BOOLEAN, getter=lambda c: c[0]),
            did_authorities_ask_for_social_media_pass=factory.Iterator(
                choices.MAYBE_BOOLEAN, getter=lambda c: c[0]),
            did_authorities_ask_about_work=factory.Iterator(
                choices.MAYBE_BOOLEAN, getter=lambda c: c[0]),
            were_devices_searched_or_seized=factory.Iterator(
                choices.MAYBE_BOOLEAN, getter=lambda c: c[0]),
        )
        physical_attack = factory.Trait(
            assailant=factory.Iterator(choices.ACTORS, getter=lambda c: c[0]),
            was_journalist_targeted=factory.Iterator(
                choices.MAYBE_BOOLEAN, getter=lambda c: c[0]),
        )
        leak_case = factory.Trait(
            # targets_whose_communications_were_obtained=2,
            charged_under_espionage_act=factory.Faker('boolean'),
        )
        subpoena = factory.Trait(
            subpoena_type=factory.Iterator(
                choices.SUBPOENA_TYPE, getter=lambda c: c[0]),
            subpoena_status=factory.Iterator(
                choices.SUBPOENA_STATUS, getter=lambda c: c[0]),
            held_in_contempt=factory.Iterator(
                choices.MAYBE_BOOLEAN, getter=lambda c: c[0]),
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

    # https://adamj.eu/tech/2014/09/03/factory-boy-fun/
    @factory.post_generation
    def targets(self, create, count):
        if count is None:
            count = 2
        make_target = getattr(TargetFactory, 'create' if create else 'build')
        targets = []
        for i in range(count):
            t = make_target()
            t.targets_incidents.add(self)
            targets.append(t)
        if not create:
            self._prefetched_objects_cache = {'targets': targets}

    @factory.post_generation
    def targets_whose_communications_were_obtained(self, create, count):
        if count is None:
            return
        make_target = getattr(TargetFactory, 'create' if create else 'build')
        targets = []
        for i in range(count):
            t = make_target()
            t.targets_communications_obtained_incidents.add(self)
            targets.append(t)
        if not create:
            self._prefetched_objects_cache = {
                'targets_whose_communications_were_obtained': targets
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


class InexactDateIncidentPageFactory(IncidentPageFactory):
    exact_date_unknown = True
    date = factory.Faker(
        'date_between',
        start_date=datetime.date(2017, 3, 1),
        end_date=datetime.date(2017, 3, 31),
    )


class IncidentCategorizationFactory(factory.DjangoModelFactory):
    class Meta:
        model = IncidentCategorization
    sort_order = factory.Sequence(lambda n: n)
    incident_page = factory.SubFactory(IncidentPageFactory)
    category = factory.SubFactory(CategoryPageFactory)


class TargetFactory(factory.DjangoModelFactory):
    class Meta:
        model = Target
        django_get_or_create = ('title',)
    title = factory.Faker('name')


class ChargeFactory(factory.DjangoModelFactory):
    class Meta:
        model = Charge
        django_get_or_create = ('title',)
    title = factory.Faker('sentence', nb_words=3)


class NationalityFactory(factory.DjangoModelFactory):
    class Meta:
        model = Nationality
        django_get_or_create = ('title',)
    title = factory.Faker('country')


class PoliticianOrPublicFactory(factory.DjangoModelFactory):
    class Meta:
        model = PoliticianOrPublic
        django_get_or_create = ('title',)
    title = factory.Faker('name')


class StateFactory(factory.DjangoModelFactory):
    class Meta:
        model = State
        django_get_or_create = ('name',)
    name = factory.Faker('state')
