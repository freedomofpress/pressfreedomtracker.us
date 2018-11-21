import factory
from faker import Faker
import wagtail_factories
from wagtail.wagtailcore.rich_text import RichText

from common.models import (
    CategoryPage,
    CategoryIncidentFilter,
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

    bio = factory.LazyAttribute(lambda _: RichText(fake.paragraph()))


class OrganizationIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = OrganizationIndexPage


class OrganizationPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = OrganizationPage

    website = factory.Faker('uri')
    description = factory.LazyAttribute(lambda _: RichText(fake.sentence()))
