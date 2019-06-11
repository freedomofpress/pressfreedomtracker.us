import factory
import wagtail_factories
from faker import Faker
from wagtail.core.rich_text import RichText

from home.models import HomePage


fake = Faker()


class HomePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = HomePage
        django_get_or_create = ('slug',)

    title = 'Home'
    about = factory.LazyAttribute(lambda _: RichText(fake.paragraph(nb_sentences=10)))

