from django.core.management.base import BaseCommand

from incident.models import PrepublicationIncidentSync
from incident.utils.sync_prepubs import sync_prepubs


class Command(BaseCommand):
    help = "Fetches data about prepublication incidents from a Google Sheet and synchronizes the web site database with the rows in the sheet."

    def handle(self, *args, **options):
        try:
            status, message = sync_prepubs()
        except Exception as e:
            message = f"Prepub sync failed: {e}"
            status = PrepublicationIncidentSync.Status.FAILED
            self.stdout.write(f"Prepub sync failed: {e}")
            raise

        sync = PrepublicationIncidentSync.objects.first()
        if not sync:
            PrepublicationIncidentSync.objects.create(
                message=message,
                status=status,
            )
        else:
            sync.message = message
            sync.status = status
            sync.save()
