from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from wagtail.core.signals import page_published
from wagtail.contrib.frontend_cache.utils import purge_page_from_cache
from wagtail.contrib.settings.models import BaseSetting

from common.models import CategoryPage, SimplePage
from cloudflare.utils import purge_tags_from_cache, purge_all_from_cache
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


@receiver([pre_delete, post_save])
def purge_cache_for_settings(sender, **kwargs):
    """
    We're using the nuclear option for caching. Every time any Setting changes
    we flush the entire cache
    """
    if issubclass(sender, BaseSetting):
        purge_all_from_cache()


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
