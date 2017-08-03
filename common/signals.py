from django.db.models.signals import post_save
from wagtail.contrib.wagtailfrontendcache.utils import purge_page_from_cache

from common.models import CategoryPage
from incident.models import IncidentPage


def purge_category_from_frontend_cache(**kwargs):
    """
    Currently this busts all the category pages' caches. If we wanted to be
    more conservative in the future, we could write a conditional to identify
    if the sender is actually an incident within this category.
    """
    for category_page in CategoryPage.objects.live():
        purge_page_from_cache(category_page)


post_save.connect(purge_category_from_frontend_cache, sender=IncidentPage)
