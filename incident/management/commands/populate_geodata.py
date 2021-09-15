from django.core.management.base import BaseCommand

from incident.models import IncidentPage
from geonames.cities import get_city_coords


class Command(BaseCommand):
    help = 'Look up and save latitude and longitude data for existing incident pages'

    def handle(self, *args, **options):
        incidents = IncidentPage.objects.filter(
            state__isnull=False,
            city__isnull=False,
        ).select_related('state')

        for incident in incidents:
            incident.latitude, incident.longitude = get_city_coords(
                incident.city, incident.state.abbreviation
            )
        IncidentPage.objects.bulk_update(incidents, ['latitude', 'longitude'])
