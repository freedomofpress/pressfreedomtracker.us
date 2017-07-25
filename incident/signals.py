from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_save

from common.models import CategoryPage
from incident.models import IncidentPage


def purge_incident_caches(sender, **kwargs):
    # Purge teaser template cache
    cache.delete(make_template_fragment_key('incident', [True, sender.pk]))
    # Purge detail template cache
    cache.delete(make_template_fragment_key('incident', [False, sender.pk]))


def purge_all_incident_caches(**kwargs):
    pages = IncidentPage.objects.all().values_list('id', flat=True)
    for pk in pages:
        # Purge teaser template cache
        cache.delete(make_template_fragment_key('incident', [True, pk]))
        # Purge detail template cache
        cache.delete(make_template_fragment_key('incident', [False, pk]))

post_save.connect(purge_incident_caches, sender=IncidentPage)
