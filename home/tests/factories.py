import factory
import wagtail_factories
from wagtail.core.rich_text import RichText

from home.models import HomePage
from common.choices import CATEGORY_COLOR_CHOICES
from common.tests.utils import StreamfieldProvider


factory.Faker.add_provider(StreamfieldProvider)


class HomePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = HomePage
        exclude = ('about_text')

    about_text = factory.Faker('paragraph', nb_sentences=10)

    title = 'Home'
    about = factory.LazyAttribute(lambda o: RichText(o.about_text))
