from django.db.models.signals import post_save
from wagtail.contrib.wagtailfrontendcache.utils import purge_page_from_cache

from common.models import CategoryPage
from incident.models import IncidentPage


def purge_incident_from_frontend_cache_for_category(
    instance=None, sender=None, **kwargs
):
    """
    Busts the cache for any incident within a category when that category
    changes.
    """
    incidents = IncidentPage.objects.filter(categories__category=instance)
    for incident in incidents:
        purge_page_from_cache(incident)


post_save.connect(
    purge_incident_from_frontend_cache_for_category,
    sender=CategoryPage
)
