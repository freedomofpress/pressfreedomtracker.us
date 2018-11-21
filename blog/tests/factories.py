from datetime import timezone

import factory
import wagtail_factories

from blog.models import BlogPage, BlogIndexPage
from common.tests.factories import PersonPageFactory, OrganizationPageFactory


class BlogIndexPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = BlogIndexPage


class BlogPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = BlogPage
    publication_datetime = factory.Faker(
        'date_time_this_month', after_now=False, before_now=True,
        tzinfo=timezone.utc)
    author = factory.SubFactory(PersonPageFactory)
    organization = factory.SubFactory(OrganizationPageFactory)
