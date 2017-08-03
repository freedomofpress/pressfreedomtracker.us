import factory
import wagtail_factories

from home.models import HomePage

class HomePageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = HomePage

    parent = factory.SubFactory(wagtail_factories.PageFactory, parent=None)
    title = factory.Sequence(lambda n: 'Category {n}'.format(n=n))
