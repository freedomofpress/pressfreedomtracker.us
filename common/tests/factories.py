import datetime

import factory
import wagtail_factories
from wagtail_factories.blocks import BlockFactory
from wagtail import blocks
from wagtail.rich_text import RichText

from common.blocks import (
    ALIGNMENT_CHOICES,
    Heading1,
    Heading2,
    Heading3,
    StyledTextBlock,
    RichTextTemplateBlock,
    AlignedCaptionedImageBlock,
    TweetEmbedBlock,
    PullQuoteBlock,
    RichTextBlockQuoteBlock,
    AlignedCaptionedEmbedBlock,
)
from common.choices import CATEGORY_SYMBOL_CHOICES
from common.models import (
    CategoryPage,
    CategoryIncidentFilter,
    ChartSnapshot,
    CategoryMethodologyItem,
    CommonTag,
    CustomImage,
    SimplePage,
    PersonPage,
    OrganizationPage,
    OrganizationIndexPage,
    TaxonomyCategoryPage,
    TaxonomySettings,
)
from common.utils.chart_pregenerator.types import (
    ChartType,
    SnapshotType,
)


class RichTextTemplateBlockFactory(BlockFactory):
    class Meta:
        model = RichTextTemplateBlock


class AlignedCaptionedImageBlockFactory(wagtail_factories.StructBlockFactory):
    image = factory.SubFactory(
        wagtail_factories.blocks.ImageChooserBlockFactory,
    )
    caption = RichText('Caption')
    alignment = ALIGNMENT_CHOICES[0][0]

    class Meta:
        model = AlignedCaptionedImageBlock


class TweetEmbedBlockFactory(wagtail_factories.StructBlockFactory):
    tweet = factory.SubFactory(wagtail_factories.blocks.CharBlockFactory)

    class Meta:
        model = TweetEmbedBlock


class RichTextBlockQuoteBlockFactory(wagtail_factories.StructBlockFactory):
    text = RichText('Quote content')
    source_text = RichText('Name of source')
    source_url = 'https://freedom.press'

    class Meta:
        model = RichTextBlockQuoteBlock


class PullQuoteBlockFactory(wagtail_factories.StructBlockFactory):
    text = 'Text of Quote'

    class Meta:
        model = PullQuoteBlock


class AlignedCaptionedEmbedBlockFactory(wagtail_factories.StructBlockFactory):
    caption = RichText('Embed caption')
    attribution = 'Attribution of embed'
    video = factory.SubFactory(wagtail_factories.blocks.CharBlockFactory)
    alignment = ALIGNMENT_CHOICES[0][0]

    class Meta:
        model = AlignedCaptionedEmbedBlock


class DevelopmentSiteFactory(wagtail_factories.SiteFactory):
    class Meta:
        django_get_or_create = ('is_default_site',)
    site_name = 'Press Freedom Tracker (Dev)'
    port = 8000
    is_default_site = True
    root_page = None


class CategoryIncidentFilterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategoryIncidentFilter

    sort_order = factory.Sequence(lambda n: n)


class TaxonomySettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TaxonomySettings
        django_get_or_create = ('site',)

    site = factory.SubFactory(DevelopmentSiteFactory)


class TaxonomyCategoryPageFactory(factory.django.DjangoModelFactory):
    taxonomy_setting = factory.SubFactory(TaxonomySettingsFactory)
    sort_order = factory.Sequence(lambda n: n)

    class Meta:
        model = TaxonomyCategoryPage


class MethodologyItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CategoryMethodologyItem

    label = 'Item Label'
    description = 'Item Description'


class CategoryPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = CategoryPage

    class Params:
        arrest = factory.Trait(
            title='Arrest / Criminal Charge',
            plural_name='Arrests and Criminal Charges',
            slug='arrest-criminal-charge'
        )
        border_stop = factory.Trait(
            title='Border Stop',
            plural_name='Border Stops',
            slug='border-stop'
        )
        denial_of_access = factory.Trait(
            title='Denial of Access',
            plural_name='Denials of Access',
            slug='denial-access',
        )
        equipment_search = factory.Trait(
            title='Equipment Search or Seizure',
            plural_name='Equipment Searches, Seizures and Damage',
            slug='equipment-search-seizure-or-damage',
        )
        assault = factory.Trait(
            title='Assault',
            plural_name='Assaults',
            slug='assault',
        )
        leak_case = factory.Trait(
            title='Leak Case',
            plural_name='Leak Cases',
            slug='leak-case'
        )
        subpoena = factory.Trait(
            title='Subpoena / Legal Order',
            plural_name='Subpoenas and Legal Orders',
            slug='subpoena'
        )
        equipment_damage = factory.Trait(
            title='Equipment Damage',
            plural_name='Equipment Damages',
            slug='equipment-damage',
        )
        other_incident = factory.Trait(
            title='Other Incident',
            plural_name='Other Incidents',
            slug='other-incident',
        )
        chilling_statement = factory.Trait(
            title='Chilling Statement',
            plural_name='Chilling Statements',
            slug='chilling-statement',
        )
        prior_restraint = factory.Trait(
            title='Prior Restraint',
            plural_name='Prior Restraints',
            slug='prior-restraint',
        )

    title = factory.Sequence(lambda n: 'Category {n}'.format(n=n))
    methodology = RichText("Methodology")
    taxonomy = factory.RelatedFactory(TaxonomyCategoryPageFactory, 'category')
    page_symbol = factory.Iterator(CATEGORY_SYMBOL_CHOICES, getter=lambda c: c[0])
    viz_type = 'none'
    methodology_item = factory.RelatedFactory(MethodologyItemFactory, 'page')
    methodology_item2 = factory.RelatedFactory(MethodologyItemFactory, 'page')

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
    attribution = factory.Sequence(lambda n: f'Attribution {n}')

    class Meta:
        model = CustomImage


class PersonPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = PersonPage

    title = factory.Sequence(lambda n: f'Person {n}')
    bio = RichText("Bio")
    website = 'https://freedom.press'
    photo = None


class OrganizationIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = OrganizationIndexPage

    title = 'All Organizations'


class OrganizationPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = OrganizationPage

    title = factory.Sequence(lambda n: f'Organization {n}')
    slug = factory.Sequence(lambda n: 'organization-{n}'.format(n=n))
    website = 'https://freedom.press'
    description = 'Organization Description'


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


class CommonTagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommonTag
        django_get_or_create = ('title',)

    title = factory.Sequence(lambda n: f'Tag {n}')


class ChartSnapshotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChartSnapshot

    class Params:
        svg = factory.Trait(
            snapshot_type=SnapshotType.SVG,
            chart_svg='<svg />',
        )
        png = factory.Trait(
            snapshot_type=SnapshotType.PNG,
            chart_image=factory.SubFactory(CustomImageFactory)
        )

    svg = True

    last_generated = datetime.datetime(2023, 1, 1, 0, 0)
    query = {}
    chart_type = ChartType.VERTICAL_BAR
