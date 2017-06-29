import factory
import wagtail_factories
from wagtail.wagtailcore.rich_text import RichText

from common.models import CategoryPage


class CategoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = CategoryPage

    parent = factory.SubFactory(wagtail_factories.PageFactory, parent=None)
    title = factory.Sequence(lambda n: 'Category {n}'.format(n=n))
    methodology = factory.Sequence(
        lambda n: RichText('Category {n}'.format(n=n))
    )
    description = factory.Sequence(
        lambda n: RichText('Category {n}'.format(n=n))
    )
