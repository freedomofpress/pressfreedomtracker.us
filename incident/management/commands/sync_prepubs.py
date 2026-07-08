from django.conf import settings
from django.core.management.base import BaseCommand

import structlog

from incident.models import PrepublicationIncidentSync, PrepublicationSyncSkippedRow
from incident.utils.sync_prepubs import sync_prepubs, PrepubSource


logger = structlog.get_logger()


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
                header_row_index=int(config["HEADER_ROW_INDEX"]),
                sheet_name=config["SHEET_NAME"],
                google_api_version=config["GOOGLE_API_VERSION"],
            )
        else:
            self.stdout.write(
                f"Prepub sync failed: could not load settings for source {name!r}"
            )
            return

        error_message = ""
        try:
            result = sync_prepubs(source)
            successful_rows = result.successful_rows
            skipped_rows = result.skipped_rows
        except Exception as e:
            self.stdout.write(f"Prepub sync failed: {e}")
            logger.exception("Prepub sync failed")
            error_message = str(e)
            successful_rows = 0
            skipped_rows = []

        structlog.contextvars.bind_contextvars(
            sync_prepubs_successful_rows=successful_rows,
            sync_prepubs_skipped_rows=len(skipped_rows),
        )
        logger.info("Prepublication sync completed")

        sync = PrepublicationIncidentSync.objects.first()
        if not sync:
            PrepublicationIncidentSync.objects.create(
                successful_rows=successful_rows,
                error_message=error_message,
            )
        else:
            sync.successful_rows = successful_rows
            sync.error_message = error_message
            sync.save()
        PrepublicationSyncSkippedRow.objects.all().delete()
        for skipped_row in skipped_rows:
            PrepublicationSyncSkippedRow.objects.bulk_create(
                [
                    PrepublicationSyncSkippedRow(
                        sync=sync, number=skipped_row.number, reason=skipped_row.reason
                    )
                ]
            )
