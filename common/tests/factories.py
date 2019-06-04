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
    SimplePage,
    PersonPage,
    OrganizationPage,
    OrganizationIndexPage,
)


fake = Faker()


class CategoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = CategoryPage

    title = factory.Sequence(lambda n: 'Category {n}'.format(n=n))
    methodology = factory.Sequence(
        lambda n: RichText('Category {n}'.format(n=n))
    )

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


class PersonPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = PersonPage

    title = factory.Faker('name')
    photo = factory.SubFactory(wagtail_factories.ImageFactory)
    bio = factory.LazyAttribute(lambda _: RichText(fake.paragraph()))
    website = factory.Faker('uri')


class OrganizationIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = OrganizationIndexPage


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
