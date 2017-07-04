import factory
import wagtail_factories
from wagtail.wagtailcore import blocks

from incident.models import (
    IncidentIndexPage,
    IncidentPage,
    IncidentCategorization,
)
from common.tests.factories import CategoryPageFactory


class BlockFactory(factory.Factory):
    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, value):
        return model_class().clean(value)

    @classmethod
    def _create(cls, model_class, value):
        return model_class().clean(value)


class RichTextBlockFactory(BlockFactory):
    class Meta:
        model = blocks.RichTextBlock


class IncidentIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = IncidentIndexPage

    parent = factory.SubFactory(wagtail_factories.PageFactory, parent=None)


class IncidentPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = IncidentPage

    parent = factory.SubFactory(IncidentIndexPageFactory)
    title = factory.Faker('sentence')
    date = factory.Faker('date')
    city = factory.Faker('city')
    body = wagtail_factories.StreamFieldFactory({
        'rich_text': RichTextBlockFactory,
        'image': wagtail_factories.ImageChooserBlockFactory,
        'raw_html': wagtail_factories.CharBlockFactory,
    })


class IncidentCategorizationFactory(factory.Factory):
    class Meta:
        model = IncidentCategorization
    sort_order = factory.Sequence(lambda n: n)
    incident_page = factory.SubFactory(IncidentPageFactory)
    category = factory.SubFactory(CategoryPageFactory)
