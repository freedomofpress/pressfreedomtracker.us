import structlog
from django.db.models.signals import post_delete
from wagtail.contrib.frontend_cache.utils import purge_page_from_cache
from wagtail.signals import page_published

from common.models import CategoryPage
from cloudflare.utils import purge_tags_from_cache
from incident.models import IncidentPage, IncidentIndexPage


logger = structlog.get_logger('wagtail.frontendcache')


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
        logger.info(
            f"Purged page IncidentPage with title: {incident.title} and slug: {incident.slug}"
        )


def purge_incident_index_from_frontend_cache(**kwargs):
    tags = []
    for incident_index_page in IncidentIndexPage.objects.live():
        purge_page_from_cache(incident_index_page)
        tags.append(incident_index_page.get_cache_tag())
        logger.info(
            f"Purged page IncidentIndexPage with title: {incident_index_page.title} and slug: {incident_index_page.slug}"
        )
    purge_tags_from_cache(tags)


# IncidentPage cache
page_published.connect(
    purge_incident_from_frontend_cache_for_category,
    sender=CategoryPage
)
post_delete.connect(
    purge_incident_from_frontend_cache_for_category,
    sender=CategoryPage
)

# IncidentIndexPage cache
page_published.connect(
    purge_incident_index_from_frontend_cache,
    sender=CategoryPage
)
page_published.connect(
    purge_incident_index_from_frontend_cache,
    sender=IncidentPage
)
post_delete.connect(
    purge_incident_index_from_frontend_cache,
    sender=IncidentPage
)
