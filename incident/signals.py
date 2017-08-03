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


def purge_incident_from_frontend_cache_for_incident(
    instance=None, sender=None, **kwargs
):
    """
    Busts the cache for any incident that shares a category or is
    a related incident to the incident just changed.
    """

    # Purge cache for related incidents
    for incident in instance.related_incidents.all():
        purge_page_from_cache(incident)

    # Purge cache for incidents that share a category and may
    # therefore show up as a related incident
    for categorization in instance.categories.all():
        purge_incident_from_frontend_cache_for_category(
            instance=categorization.category
        )


post_save.connect(
    purge_incident_from_frontend_cache_for_category,
    sender=CategoryPage
)
post_save.connect(
    purge_incident_from_frontend_cache_for_incident,
    sender=IncidentPage
)
