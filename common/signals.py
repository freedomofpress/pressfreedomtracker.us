from django.db.models.signals import post_save
from wagtail.contrib.wagtailfrontendcache.utils import purge_page_from_cache

from common.models import CategoryPage, SimplePage
from incident.models import IncidentPage
from home.models import HomePage
from blog.models import BlogPage


def purge_category_from_frontend_cache(**kwargs):
    """
    Currently this busts all the category pages' caches. If we wanted to be
    more conservative in the future, we could write a conditional to identify
    if the sender is actually an incident within this category.
    """
    for category_page in CategoryPage.objects.live():
        purge_page_from_cache(category_page)


def purge_simple_page_from_frontend_cache(**kwargs):
    for simple_page in SimplePage.objects.live():
        purge_page_from_cache(simple_page)


post_save.connect(purge_category_from_frontend_cache, sender=IncidentPage)

# Some simple pages have sidebar content from incidents,
# blogs, and the homepage
post_save.connect(purge_simple_page_from_frontend_cache, sender=IncidentPage)
post_save.connect(purge_simple_page_from_frontend_cache, sender=BlogPage)
post_save.connect(purge_simple_page_from_frontend_cache, sender=HomePage)
