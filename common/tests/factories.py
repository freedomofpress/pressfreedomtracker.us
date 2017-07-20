import factory
from faker import Faker
import wagtail_factories
from wagtail.wagtailcore.rich_text import RichText

from common.models import (
    CategoryPage,
    PersonPage,
    OrganizationPage,
    OrganizationIndexPage,
)


fake = Faker()


class CategoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = CategoryPage

    parent = factory.SubFactory(wagtail_factories.PageFactory, parent=None)
    title = factory.Sequence(lambda n: 'Category {n}'.format(n=n))
    methodology = factory.Sequence(
        lambda n: RichText('Category {n}'.format(n=n))
    )


class PersonPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = PersonPage

    parent = factory.SubFactory(wagtail_factories.PageFactory, parent=None)
    bio = factory.LazyAttribute(lambda _: RichText(fake.paragraph()))


class OrganizationIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = OrganizationIndexPage
    parent = factory.SubFactory(wagtail_factories.PageFactory, parent=None)


class OrganizationPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = OrganizationPage

    parent = factory.SubFactory(OrganizationIndexPageFactory)
    website = factory.Faker('uri')
    description = factory.LazyAttribute(lambda _: RichText(fake.sentence()))
