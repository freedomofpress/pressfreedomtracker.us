import random
from datetime import timezone
from faker import Faker

import factory
import wagtail_factories

from blog.models import BlogPage, BlogIndexPage
from common.tests.factories import (
    PersonPageFactory,
    OrganizationPageFactory,
    RawHTMLBlockFactory,
    RichTextBlockFactory,
    Heading1Factory,
    Heading2Factory,
    Heading3Factory,
    StyledTextBlockFactory,
)


fake = Faker()


class BlogIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = BlogIndexPage
    title = 'PFT Blog'
    about_blog_title = 'The blog of the press freedom tracker'
    body = wagtail_factories.StreamFieldFactory({
        'image': wagtail_factories.ImageChooserBlockFactory,
        'raw_html': RawHTMLBlockFactory,
        'rich_text': RichTextBlockFactory,
    })


class BlogPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = BlogPage

    title = factory.Sequence(
        lambda n: fake.text(random.randint(5, 58))[:-1] + ' ({})'.format(n)
    )
    body = wagtail_factories.StreamFieldFactory({
        'heading_1': Heading1Factory,
        'heading_2': Heading2Factory,
        'heading_3': Heading3Factory,
        'text': StyledTextBlockFactory,
    })
    teaser_text = factory.Faker('sentence')
    publication_datetime = factory.Faker(
        'date_time_this_month', after_now=False, before_now=True,
        tzinfo=timezone.utc)
    author = factory.SubFactory(PersonPageFactory)
    organization = factory.SubFactory(OrganizationPageFactory)
