import factory
import wagtail_factories
from faker import Faker
from wagtail.core import blocks
from wagtail.core.rich_text import RichText

from common.blocks import (
    Heading1,
    Heading2,
    Heading3,
    StyledTextBlock,
)
from common.models import (
    CategoryPage,
    CategoryIncidentFilter,
    CustomImage,
    SimplePage,
    PersonPage,
    OrganizationPage,
    OrganizationIndexPage,
    TaxonomyCategoryPage,
    TaxonomySettings,
)


fake = Faker()


class DevelopmentSiteFactory(wagtail_factories.SiteFactory):
    class Meta:
        django_get_or_create = ('is_default_site',)
    site_name = 'Press Freedom Tracker (Dev)'
    port = 8000
    is_default_site = True
    root_page = None


class CategoryIncidentFilterFactory(factory.DjangoModelFactory):
    class Meta:
        model = CategoryIncidentFilter

    sort_order = factory.Sequence(lambda n: n)


class TaxonomySettingsFactory(factory.DjangoModelFactory):
    class Meta:
        model = TaxonomySettings
        django_get_or_create = ('site',)

    site = factory.SubFactory(DevelopmentSiteFactory)


class TaxonomyCategoryPageFactory(factory.DjangoModelFactory):
    taxonomy_setting = factory.SubFactory(TaxonomySettingsFactory)
    sort_order = factory.Sequence(lambda n: n)

    class Meta:
        model = TaxonomyCategoryPage


class CategoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = CategoryPage

    class Params:
        arrest = factory.Trait(
            title='Arrest / Criminal Charge',
            plural_name='Arrests and Criminal Charges',
        )
        border_stop = factory.Trait(
            title='Border Stop',
            plural_name='Border Stops',
        )
        denied_access = factory.Trait(
            title='Denial of Access',
            plural_name='Denials of Access',
        )
        equipment_search = factory.Trait(
            title='Equipment Search or Seizure',
            plural_name='Equipment Searches, Seizures and Damage',
        )
        physical_attack = factory.Trait(
            title='Physical Attack',
            plural_name='Physical Attacks',
        )
        leak = factory.Trait(
            title='Leak Case',
            plural_name='Leak Cases',
        )
        subpoena = factory.Trait(
            title='Subpoena / Legal Order',
            plural_name='Subpoenas and Legal Orders',
        )

    title = factory.Sequence(lambda n: 'Category {n}'.format(n=n))
    methodology = factory.LazyAttribute(lambda _: RichText(fake.paragraph(nb_sentences=5)))
    taxonomy = factory.RelatedFactory(TaxonomyCategoryPageFactory, 'category')

    @factory.post_generation
    def incident_filters(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            CategoryIncidentFilter.objects.bulk_create([
                CategoryIncidentFilter(
                    category=self,
                    incident_filter=incident_filter,
                )
                for incident_filter in extracted
            ])


class CustomImageFactory(wagtail_factories.ImageFactory):
    attribution = factory.Faker('name')

    class Meta:
        model = CustomImage


class PersonPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = PersonPage

    title = factory.Faker('name')
    bio = factory.LazyAttribute(lambda _: RichText(fake.paragraph()))
    website = factory.Faker('uri')
    photo = None


class OrganizationIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = OrganizationIndexPage
        django_get_or_create = ('slug',)
    title = 'All Organizations'


class OrganizationPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = OrganizationPage

    title = factory.Faker('company')
    website = factory.Faker('uri')
    description = factory.Faker('catch_phrase')


class SimplePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = SimplePage


class RichTextBlockFactory(wagtail_factories.blocks.BlockFactory):
    class Meta:
        model = blocks.RichTextBlock


class RawHTMLBlockFactory(wagtail_factories.blocks.BlockFactory):
    class Meta:
        model = blocks.RawHTMLBlock


class ChoiceBlockFactory(wagtail_factories.blocks.BlockFactory):
    class Meta:
        model = blocks.ChoiceBlock


class Heading1Factory(wagtail_factories.StructBlockFactory):
    content = wagtail_factories.CharBlockFactory

    class Meta:
        model = Heading1


class Heading2Factory(wagtail_factories.StructBlockFactory):
    content = wagtail_factories.CharBlockFactory

    class Meta:
        model = Heading2


class Heading3Factory(wagtail_factories.StructBlockFactory):
    content = wagtail_factories.CharBlockFactory

    class Meta:
        model = Heading3


class StyledTextBlockFactory(wagtail_factories.StructBlockFactory):
    class Meta:
        model = StyledTextBlock

    text = RichTextBlockFactory
    background_color = ChoiceBlockFactory
    text_align = ChoiceBlockFactory
    font_size = ChoiceBlockFactory
    font_family = ChoiceBlockFactory
