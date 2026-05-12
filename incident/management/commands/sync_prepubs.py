from django.conf import settings
from django.core.management.base import BaseCommand

from incident.models import PrepublicationIncidentSync
from incident.utils.sync_prepubs import sync_prepubs, PrepubSource


class Command(BaseCommand):
    help = "Fetches data about prepublication incidents from a Google Sheet and synchronizes the web site database with the rows in the sheet."

    def handle(self, *args, **options):
        prepub_sources_settings = getattr(settings, "PREPUBLICATION_SOURCES", {})
        name = "default"  # This can eventually become a command argument

        config = prepub_sources_settings.get(name, {})
        if config:
            source = PrepubSource(
                google_sheets_credentials=config["GOOGLE_SHEETS_CREDS"],
                document_id=config["DOCUMENT_ID"],
                google_api_version=config["GOOGLE_API_VERSION"],
            )
        else:
            self.stdout.write(
                f"Prepub sync failed: could not load settings for source {name!r}"
            )
            return

        try:
            status, message = sync_prepubs(source)
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
