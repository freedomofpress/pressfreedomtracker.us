import factory
import wagtail_factories

from home.models import HomePage


class HomePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = HomePage

    title = factory.Sequence(lambda n: 'Home {n}'.format(n=n))
