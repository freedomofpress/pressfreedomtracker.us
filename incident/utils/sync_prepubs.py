import json
from dataclasses import dataclass
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from common.models import CategoryPage
from geonames.models import GeoName
from incident.models import (
    PrepublicationIncident,
    PrepublicationIncidentCategory,
)


@dataclass
class PrepubSource:
    google_sheets_credentials: str
    document_id: str
    sheet_name: str
    header_row_index: int
    google_api_version: str


@dataclass
class DateParseResult:
    value: datetime.date
    precision: int


@dataclass
class SkippedRow:
    number: int
    reason: str


@dataclass
class PrepubSyncResult:
    skipped_rows: list[SkippedRow]
    successful_rows: int


class DateParseError(Exception):
    pass


def authenticate_service(source: PrepubSource):
    account_info = json.loads(source.google_sheets_credentials)

    creds = Credentials.from_service_account_info(
        account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    return build("sheets", source.google_api_version, credentials=creds)


def fetch_sheet_data(source: PrepubSource):
    sheet = authenticate_service(source).spreadsheets()
    result = (
        sheet.values()
        .get(
            spreadsheetId=source.document_id,
            range=source.sheet_name,
        )
        .execute()
    )
    return result.get("values", [])


def parse_date(text: str) -> DateParseResult:
    try:
        parsed = datetime.strptime(text, "%m/%d/%Y").date()
        return DateParseResult(
            value=parsed, precision=PrepublicationIncident.DatePrecision.DAY
        )
    except ValueError:
        pass

    try:
        parsed = datetime.strptime(text, "%m/%Y").date()
        return DateParseResult(
            value=parsed, precision=PrepublicationIncident.DatePrecision.MONTH
        )
    except ValueError:
        raise DateParseError


def sync_prepubs(source: PrepubSource):
    values = fetch_sheet_data(source)

    prepubs = []
    skipped_rows = []
    prepub_categories = []
    header = values[source.header_row_index]
    data_start_index = source.header_row_index + 1

    idx_status = header.index("Status")
    idx_type = header.index("Type")
    idx_team = header.index("Team")
    idx_city = header.index("City")
    idx_state = header.index("State")
    idx_categories = header.index("Categories")
    idx_incident_date = header.index("Incident Date")

    rest = values[data_start_index:]

    for i, row in enumerate(rest):
        # When displaying the row number in output messages, that
        # number should reference the row in the original Google
        # sheet, so it can be debugged by a person who can look at
        # that document manually.  We add 1 here to convert from
        # zero-based Python iterators to one-based Google Sheets rows.
        row_number = i + data_start_index + 1

        if (
            row[idx_status] == "Published"
            or row[idx_team] != "USPFT"
            or row[idx_type] != "USPFT Incident"
            or row[idx_categories] == "Update"
        ):
            continue

        # Categories
        categories_text = [c.strip() for c in row[idx_categories].split(",")]
        categories = []
        category_errors = []
        for category_name in categories_text:
            try:
                categories.append(
                    CategoryPage.objects.get(google_sheets_name=category_name)
                )
            except CategoryPage.DoesNotExist:
                category_errors.append(f'Invalid category "{category_name}"')

        if category_errors:
            skipped_rows.append(
                SkippedRow(number=row_number, reason="; ".join(category_errors))
            )
            continue

        # Date
        try:
            parsed_date = parse_date(row[idx_incident_date])
        except DateParseError:
            skipped_rows.append(
                SkippedRow(
                    number=row_number, reason=f'Invalid date "{row[idx_incident_date]}"'
                )
            )
            continue

        # Location
        if row[idx_city] == "Washington, D.C.":
            # Handle the case where the formatting used for Washington
            # DC in the spreadsheet doesn't quite match how it's
            # encoded in the GeoNames database.
            city = "Washington"
            regcode = "DC"
        else:
            city = row[idx_city].strip()
            regcode = row[idx_state].strip()
        try:
            geoname = GeoName.objects.get(name=city, regcode=regcode)
        except GeoName.DoesNotExist:
            skipped_rows.append(
                SkippedRow(
                    number=row_number, reason=f'Invalid location "{city}, {regcode}"'
                )
            )
            continue

        incident = PrepublicationIncident(
            date=parsed_date.value,
            date_precision=parsed_date.precision,
            location=geoname,
        )
        for item in categories:
            prepub_categories.append(
                PrepublicationIncidentCategory(
                    category=item,
                    incident=incident,
                )
            )
        prepubs.append(incident)
    PrepublicationIncident.objects.all().delete()
    PrepublicationIncident.objects.bulk_create(prepubs)
    PrepublicationIncidentCategory.objects.bulk_create(prepub_categories)
    num_created = len(prepubs)
    return PrepubSyncResult(successful_rows=num_created, skipped_rows=skipped_rows)
