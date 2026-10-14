from urllib.parse import urljoin

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse

from wagtail.contrib.frontend_cache.utils import PurgeBatch
from wagtail.models import Site
from wagtail.signals import page_published, page_unpublished

import structlog

from cloudflare.utils import purge_tags_from_cache, purge_urls_from_cache
from common.models import CategoryPage
from home.models import HomePage
from incident.models import (
    IncidentIndexPage,
    IncidentPage,
    PrepublicationSettings,
)


logger = structlog.get_logger("wagtail.frontendcache")


def purge_incident_from_frontend_cache_for_category(
    instance=None, sender=None, **kwargs
):
    """
    Busts the cache for any incident within a category when that category
    changes.
    """
    incidents = IncidentPage.objects.filter(categories__category=instance)
    batch = PurgeBatch()
    for incident in incidents:
        batch.add_page(incident)
        logger.info(
            f"Purged page IncidentPage with title: {incident.title} and slug: {incident.slug}"
        )
    batch.purge()


def purge_incident_index_from_frontend_cache(**kwargs):
    tags = []
    batch = PurgeBatch()
    for incident_index_page in IncidentIndexPage.objects.live():
        batch.add_page(incident_index_page)
        tags.append(incident_index_page.get_cache_tag())
        logger.info(
            f"Purged page IncidentIndexPage with title: {incident_index_page.title} and slug: {incident_index_page.slug}"
        )
    batch.purge()
    purge_tags_from_cache(tags)


@receiver(pre_save, sender=PrepublicationSettings)
def stash_prepub_enabled_state(instance=None, **kwargs):
    if instance.pk is None:
        previous = PrepublicationSettings._meta.get_field("is_enabled").get_default()
    else:
        previous = (
            PrepublicationSettings.objects.filter(pk=instance.pk)
            .values_list("is_enabled", flat=True)
            .first()
        )
    instance._previously_enabled = previous


@receiver(post_save, sender=PrepublicationSettings)
def purge_prepub_list_homepage_from_frontend_cache(instance=None, **kwargs):
    previously_enabled = getattr(instance, "_previously_enabled", None)
    if previously_enabled == instance.is_enabled:
        return

    # Purge prepub list page
    path = reverse("prepub_list")
    urls = [urljoin(site.root_url, path) for site in Site.objects.all()]
    purge_urls_from_cache(urls)
    logger.info(f"Purged URLs from cache: {urls}")

    # Purge homepage
    batch = PurgeBatch()
    batch.add_pages(HomePage.objects.live())
    batch.purge()


# IncidentPage cache
page_published.connect(
    purge_incident_from_frontend_cache_for_category, sender=CategoryPage
)
page_unpublished.connect(
    purge_incident_from_frontend_cache_for_category, sender=CategoryPage
)

# IncidentIndexPage cache
page_published.connect(purge_incident_index_from_frontend_cache, sender=CategoryPage)
page_published.connect(purge_incident_index_from_frontend_cache, sender=IncidentPage)
page_unpublished.connect(purge_incident_index_from_frontend_cache, sender=IncidentPage)
