from django.db.models.signals import post_delete
from wagtail.wagtailcore.signals import page_published
from wagtail.contrib.wagtailfrontendcache.utils import purge_page_from_cache

from common.models import CategoryPage, SimplePage
from cloudflare.utils import purge_tags_from_cache
from incident.models import IncidentPage
from home.models import HomePage
from blog.models import BlogPage


def purge_category_from_frontend_cache(**kwargs):
    """
    Currently this busts all the category pages' caches. If we wanted to be
    more conservative in the future, we could write a conditional to identify
    if the sender is actually an incident within this category.
    """
    tags = []
    for category_page in CategoryPage.objects.live():
        purge_page_from_cache(category_page)
        tags.append(category_page.get_cache_tag())
    purge_tags_from_cache(tags)


def purge_simple_page_from_frontend_cache(**kwargs):
    for simple_page in SimplePage.objects.live():
        purge_page_from_cache(simple_page)


page_published.connect(purge_category_from_frontend_cache, sender=IncidentPage)
post_delete.connect(purge_category_from_frontend_cache, sender=IncidentPage)

# Some simple pages have sidebar content from incidents,
# blogs, and the homepage
page_published.connect(purge_simple_page_from_frontend_cache, sender=IncidentPage)
page_published.connect(purge_simple_page_from_frontend_cache, sender=BlogPage)
page_published.connect(purge_simple_page_from_frontend_cache, sender=HomePage)
post_delete.connect(purge_simple_page_from_frontend_cache, sender=IncidentPage)
post_delete.connect(purge_simple_page_from_frontend_cache, sender=BlogPage)
post_delete.connect(purge_simple_page_from_frontend_cache, sender=HomePage)
