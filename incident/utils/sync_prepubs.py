import json
from datetime import datetime

from django.conf import settings

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from common.models import CategoryPage
from geonames.models import GeoName
from incident.models import (
    PrepublicationIncident,
    PrepublicationIncidentCategory,
    PrepublicationIncidentSync,
)


SPREADSHEET_ID = "1PeMPpol5d0MrF0KH36ZviN7Z4PipK6ZeSDh9AlJ3-eA"


def authenticate_service():
    account_info = json.loads(settings.GOOGLE_SHEETS_CREDS)

    creds = Credentials.from_service_account_info(
        account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    return build("sheets", "v4", credentials=creds)


def fetch_sheet_data():
    sheet = authenticate_service().spreadsheets()
    result = (
        sheet.values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range="A2:Z5299",
        )
        .execute()
    )
    return result.get("values", [])


def sync_prepubs():
    values = fetch_sheet_data()

    prepubs = []
    prepub_categories = []
    errors = []
    header = values[0]

    idx_status = header.index("Status")
    idx_type = header.index("Type")
    idx_team = header.index("Team")
    idx_city = header.index("City")
    idx_state = header.index("State")
    idx_categories = header.index("Categories")
    idx_incident_date = header.index("Incident Date")

    rest = values[1:]

    for i, row in enumerate(rest):
        # When displaying the row number in output messages, that
        # number should reference the row in the original Google
        # sheet, so it can be debugged by a person who can look at
        # that document manually.  We must add 3 here since we are
        # skipping one for the header and also only looking at cells
        # in the range A2 and below, and `i` starts at 0.
        row_number = i + 3

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
                category_errors.append(
                    f'Row {row_number}: Invalid category "{category_name}"'
                )

        if category_errors:
            errors.extend(category_errors)
            continue

        # Date
        try:
            parsed_date = datetime.strptime(row[idx_incident_date], "%m/%d/%Y").date()
        except ValueError:
            errors.append(f'Row {row_number}: Invalid date "{row[idx_incident_date]}"')
            continue

        # Location
        if row[idx_city] == "Washington, D.C.":
            # Handle the case where the formatting used for Washington
            # DC in the spreadsheet doesn't quite match how it's
            # encoded in the GeoNames database.
            city = "Washington"
            regcode = "DC"
        else:
            city = row[idx_city]
            regcode = row[idx_state]
        try:
            geoname = GeoName.objects.get(name=city, regcode=regcode)
        except GeoName.DoesNotExist:
            errors.append(f'Row {row_number}: Invalid location "{city}, {regcode}"')
            continue

        incident = PrepublicationIncident(date=parsed_date, location=geoname)
        for item in categories:
            prepub_categories.append(
                PrepublicationIncidentCategory(
                    category=item,
                    incident=incident,
                )
            )
        prepubs.append(incident)
    if errors:
        return (PrepublicationIncidentSync.Status.INVALID_DATA, "\n".join(errors))
    else:
        PrepublicationIncident.objects.all().delete()
        PrepublicationIncident.objects.bulk_create(prepubs)
        PrepublicationIncidentCategory.objects.bulk_create(prepub_categories)
        num_created = len(prepubs)
        return (
            PrepublicationIncidentSync.Status.SUCCESS,
            f"{num_created} prepubs retrieved.",
        )
