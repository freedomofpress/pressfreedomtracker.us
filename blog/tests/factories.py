import random
from datetime import timezone
from faker import Faker

import factory
import wagtail_factories

from blog.models import BlogPage, BlogIndexPage
from common.tests.factories import (
    PersonPageFactory,
    OrganizationPageFactory,
)
from common.tests.utils import StreamfieldProvider
from menus.factories import MainMenuItemFactory

fake = Faker()
factory.Faker.add_provider(StreamfieldProvider)


class BlogIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = BlogIndexPage

    title = 'PFT Blog'
    about_blog_title = 'The blog of the press freedom tracker'
    body = factory.Faker('streamfield', fields=['raw_html', 'rich_text'])

    class Params:
        main_menu = factory.Trait(
            menu=factory.RelatedFactory(MainMenuItemFactory, 'link_page', for_page=True)
        )
        with_image = factory.Trait(
            body=factory.Faker('streamfield', fields=['bare_image', 'raw_html', 'rich_text'])
        )


class BlogPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = BlogPage

    class Params:
        # for use with the createdevdata command
        with_image = factory.Trait(
            teaser_graphic=factory.Faker(
                'streamfield',
                fields=['bare_image'],
            ),
            body=factory.Faker(
                'streamfield',
                fields=[
                    'heading1',
                    'heading2',
                    'heading3',
                    'styled_text_paragraphs',
                    'raw_html',
                    'styled_text',
                    'blockquote',
                    'styled_text',
                    'aside',
                    'list',
                    'styled_text',
                    'vertical_bar_chart',
                    'tree_map_chart',
                    'bubble_map_chart',
                ],
            )
        )
        with_teaser_chart = factory.Trait(
            teaser_graphic=factory.Faker(
                'streamfield',
                fields=['vertical_bar_chart'],
            ),
        )

    title = factory.Sequence(
        lambda n: fake.text(random.randint(5, 58))[:-1] + ' ({})'.format(n)
    )
    body = factory.Faker(
        'streamfield',
        fields=[
            'heading1',
            'heading2',
            'heading3',
            'raw_html',
            'styled_text',
            'blockquote',
            'styled_text',
            'list',
            'styled_text',
            'vertical_bar_chart',
            'tree_map_chart',
            'bubble_map_chart',
        ],
    )
    lead_graphic = factory.Faker('streamfield', fields=['vertical_bar_chart'])
    teaser_text = factory.Faker(
        'paragraph',
        nb_sentences=3,
        variable_nb_sentences=True,
    )
    publication_datetime = factory.Faker(
        'date_time_this_month', after_now=False, before_now=True, tzinfo=timezone.utc
    )
    first_published_at = factory.LazyAttribute(lambda o: o.publication_datetime)
    author = factory.SubFactory(PersonPageFactory)
    organization = factory.SubFactory(OrganizationPageFactory)
