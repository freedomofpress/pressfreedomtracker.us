import logging

from django.db.models.signals import post_delete
from wagtail.core.signals import page_published
from wagtail.contrib.frontend_cache.utils import purge_page_from_cache

from common.models import CategoryPage
from home.models import HomePage
from incident.models import IncidentPage, IncidentIndexPage
from blog.models import BlogPage, BlogIndexPage


logger = logging.getLogger("wagtail.frontendcache")


def purge_homepage_from_frontend_cache(**kwargs):
    for home_page in HomePage.objects.live():
        purge_page_from_cache(home_page)
        logger.info(
            f"Purged page HomePage with title: {home_page.title} and slug: {home_page.slug}"
        )


# We're being very generous with which signals cause invalidation. If we need
# more aggressive caching, we could narrow these down, either in these
# connections or by adding some conditionals to the receiver function
# (e.g., only purge if the sender is actually going to appear on the homepage)
page_published.connect(purge_homepage_from_frontend_cache, sender=CategoryPage)
page_published.connect(purge_homepage_from_frontend_cache, sender=IncidentPage)
page_published.connect(purge_homepage_from_frontend_cache, sender=IncidentIndexPage)
page_published.connect(purge_homepage_from_frontend_cache, sender=BlogPage)
page_published.connect(purge_homepage_from_frontend_cache, sender=BlogIndexPage)
post_delete.connect(purge_homepage_from_frontend_cache, sender=CategoryPage)
post_delete.connect(purge_homepage_from_frontend_cache, sender=IncidentPage)
post_delete.connect(purge_homepage_from_frontend_cache, sender=IncidentIndexPage)
post_delete.connect(purge_homepage_from_frontend_cache, sender=BlogPage)
post_delete.connect(purge_homepage_from_frontend_cache, sender=BlogIndexPage)
