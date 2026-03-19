import datetime
import json
from unittest import mock

from django.test import TestCase, override_settings

from wagtail.models import Site

from common.models import CategoryPage
from geonames.models import GeoName
from incident.models import (
    PrepublicationIncident,
    PrepublicationIncidentCategory,
    PrepublicationIncidentSync,
)
from incident.utils.sync_prepubs import (
    authenticate_service,
    fetch_sheet_data,
    sync_prepubs,
)


FAKE_CREDENTIALS = json.dumps({"private_key": "fake"})


class TestSyncPrepubs(TestCase):
    fixtures = ["cities5000-us-only.json.xz"]

    data = [
        [
            "Team",
            "Type",
            "Author",
            "Editor",
            "Slug",
            "Status",
            "Priority",
            "Editor notes",
            "",
            "Categories",
            "Incident Date",
            "Incident Year",
            "City",
            "State",
            "Journalist",
            "Outlet",
            "Incident Description",
            "Add'l Targets",
            "",
            "Website",
            "Pub Date",
            "URL",
            "Title",
            "Pub Day",
            "Pub Month",
            "Pub Quarter",
        ],
        [
            "Advocacy",
            "Newsletter",
            "Person 1",
            "Person 2",
            "Advo_email_03102026",
            "In Progress",
            "High",
            "Some notes",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "FALSE",
            "",
            "Freedom.press",
            "3/10/2026",
            "https://freedom.press/about/announcements/freedom-of-press/",
            "Press Freedom Etc.",
            "Tuesday",
            "March",
            "1",
        ],
        [
            "USPFT",
            "Newsletter",
            "Person 1",
            "Person 2",
            "Advo_email_03102026",
            "Published",
            "High",
            "Some notes",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "FALSE",
            "",
            "Freedom.press",
            "3/10/2026",
            "https://freedom.press/about/announcements/freedom-of-press/",
            "Press Freedom Etc.",
            "Tuesday",
            "March",
            "1",
        ],
        # A valid prepub row.
        [
            "USPFT",
            "USPFT Incident",
            "Person 1",
            "",
            "SLUG_01-2026",
            "Thinking",
            "High",
            "",
            "",
            "Prior Restraint",
            "1/26/2026",
            "2026",
            "Minneapolis",
            "MN",
            "Tom Hudson",
            "Independent",
            "Description",
            "FALSE",
            "",
            "",
            "",
            "",
            "",
            "Saturday",
            "December",
            "4",
        ],
    ]

    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.category_prior_restraint = CategoryPage(
            title="Test Prior Restraint",
            google_sheets_name="Prior Restraint",
        )
        cls.category_equipment = CategoryPage(
            title="Test Equipment Search/Seizure",
            google_sheets_name="Equipment Search/Seizure",
        )
        site.root_page.add_child(instance=cls.category_prior_restraint)
        site.root_page.add_child(instance=cls.category_equipment)

    def create_row(
        self,
        *,
        status="In Progress",
        team="USPFT",
        city="Albuquerque",
        state="NM",
        categories="Prior Restraint",
        incident_date="3/9/2026",
        pub_type="USPFT Incident",
    ):
        """Return a valid data row with mimicking the Google Sheets data."""
        return [
            team,
            pub_type,
            "Person 1",
            "",
            "SLUG_01-2026",
            status,
            "High",
            "",
            "",
            categories,
            incident_date,
            "2026",
            city,
            state,
            "Tom Hudson",
            "Independent",
            "Description",
            "FALSE",
            "",
            "",
            "",
            "",
            "",
            "Saturday",
            "December",
            "4",
        ]

    @override_settings(GOOGLE_SHEETS_CREDS=FAKE_CREDENTIALS)
    @mock.patch("incident.utils.sync_prepubs.build")
    @mock.patch("incident.utils.sync_prepubs.Credentials")
    def test_authenticate_service(self, mock_credentials, mock_build):
        creds = "creds"
        mock_credentials.from_service_account_info.return_value = creds
        authenticate_service()

        mock_credentials.from_service_account_info.assert_called_once_with(
            json.loads(FAKE_CREDENTIALS),
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
        )

        self.assertEqual(mock_build.call_count, 1)
        mock_build.assert_called_once_with(
            "sheets",
            "v4",
            credentials=creds,
        )

    @mock.patch("incident.utils.sync_prepubs.authenticate_service")
    def test_fetch_sheet_data(self, mock_service):
        mock_service.return_value.spreadsheets().values().get().execute.return_value = {
            "values": ["test"]
        }
        sheet_data = fetch_sheet_data()

        self.assertEqual(sheet_data, ["test"])
        mock_service.assert_has_calls(
            [
                mock.call()
                .spreadsheets()
                .values()
                .get(
                    spreadsheetId="1PeMPpol5d0MrF0KH36ZviN7Z4PipK6ZeSDh9AlJ3-eA",
                    range="A2:Z5299",
                ),
            ]
        )

    @mock.patch("incident.utils.sync_prepubs.fetch_sheet_data")
    def test_sync_prepubs_invalid_date(self, mock_fetch):
        mock_fetch.return_value = self.data + [
            self.create_row(incident_date="Jan 01, 2024")
        ]
        _, message = sync_prepubs()

        self.assertIn(
            'Row 6: Invalid date "Jan 01, 2024"',
            message,
        )

    @mock.patch("incident.utils.sync_prepubs.fetch_sheet_data")
    def test_sync_prepubs_invalid_location(self, mock_fetch):
        mock_fetch.return_value = self.data + [
            self.create_row(city="Invalid City", state="IV")
        ]
        _, message = sync_prepubs()
        self.assertIn(
            'Row 6: Invalid location "Invalid City, IV"',
            message,
        )

    @mock.patch("incident.utils.sync_prepubs.fetch_sheet_data")
    def test_sync_prepubs_invalid_washington_dc(self, mock_fetch):
        mock_fetch.return_value = self.data + [
            self.create_row(city="Washington, D.C.", state="")
        ]
        sync_prepubs()
        PrepublicationIncident.objects.prefetch_related(
            "categorizations__category",
        ).get(location__name="Washington", location__regcode="DC")

    @mock.patch("incident.utils.sync_prepubs.fetch_sheet_data")
    def test_sync_prepubs_invalid_category(self, mock_fetch):
        mock_fetch.return_value = self.data + [self.create_row(categories="Invalid")]
        status, message = sync_prepubs()
        self.assertEqual(status, PrepublicationIncidentSync.Status.INVALID_DATA)
        self.assertIn(
            'Row 6: Invalid category "Invalid"',
            message,
        )

    @mock.patch("incident.utils.sync_prepubs.fetch_sheet_data")
    def test_sync_prepubs_invalid_category_and_other_invalid_data(self, mock_fetch):
        mock_fetch.return_value = self.data + [
            self.create_row(categories="Invalid", city="Invalid")
        ]
        status, message = sync_prepubs()
        self.assertEqual(status, PrepublicationIncidentSync.Status.INVALID_DATA)

        # Category error should take precedence.
        self.assertIn(
            'Row 6: Invalid category "Invalid"',
            message,
        )

    @mock.patch("incident.utils.sync_prepubs.fetch_sheet_data")
    def test_sync_prepubs_multiple_categories(self, mock_fetch):
        mock_fetch.return_value = self.data + [
            self.create_row(
                incident_date="1/15/2026",
                categories="Prior Restraint, Equipment Search/Seizure",
            )
        ]
        status, _ = sync_prepubs()
        self.assertEqual(status, PrepublicationIncidentSync.Status.SUCCESS)

        prepub = PrepublicationIncident.objects.prefetch_related(
            "categorizations__category",
        ).get(date=datetime.date(2026, 1, 15))

        categories = (
            PrepublicationIncidentCategory.objects.filter(
                incident=prepub,
            )
            .distinct()
            .values_list("category", flat=True)
        )

        self.assertEqual(
            [self.category_prior_restraint.pk, self.category_equipment.pk],
            list(categories),
        )

    @mock.patch("incident.utils.sync_prepubs.fetch_sheet_data")
    def test_ignores_analysis_type_rows(self, mock_fetch):
        mock_fetch.return_value = self.data + [
            self.create_row(
                pub_type="USPFT Analysis",
                categories="Analysis",
                city="",
                state="",
            )
        ]
        status, _ = sync_prepubs()
        self.assertEqual(status, PrepublicationIncidentSync.Status.SUCCESS)

    @mock.patch("incident.utils.sync_prepubs.fetch_sheet_data")
    def test_sync_prepubs(self, mock_fetch):
        existing_prepub = PrepublicationIncident.objects.create(
            date=datetime.date(2025, 12, 31),
            location=GeoName.objects.get(
                name="Madison",
                regcode="WI",
            ),
        )
        existing_prepub_category = PrepublicationIncidentCategory.objects.create(
            incident=existing_prepub,
            category=self.category_prior_restraint,
        )

        mock_fetch.return_value = self.data
        sync_prepubs()

        prepub = PrepublicationIncident.objects.prefetch_related(
            "categorizations__category",
        ).get()
        self.assertEqual(prepub.date, datetime.date(2026, 1, 26))
        self.assertEqual(
            prepub.location,
            GeoName.objects.get(
                name="Minneapolis",
                regcode="MN",
            ),
        )
        self.assertEqual(
            prepub.categorizations.first().category,
            self.category_prior_restraint,
        )

        with self.assertRaises(PrepublicationIncident.DoesNotExist):
            PrepublicationIncident.objects.get(pk=existing_prepub.pk)

        with self.assertRaises(PrepublicationIncidentCategory.DoesNotExist):
            PrepublicationIncidentCategory.objects.get(pk=existing_prepub_category.pk)

    @mock.patch("incident.utils.sync_prepubs.fetch_sheet_data")
    def test_sync_prepubs_keeps_existing_if_errors(self, mock_fetch):
        existing_prepub = PrepublicationIncident.objects.create(
            date=datetime.date(2025, 12, 31),
            location=GeoName.objects.get(
                name="Madison",
                regcode="WI",
            ),
        )
        existing_prepub_category = PrepublicationIncidentCategory.objects.create(
            incident=existing_prepub,
            category=self.category_prior_restraint,
        )
        PrepublicationIncidentCategory.objects.get(pk=existing_prepub_category.pk)

        mock_fetch.return_value = self.data + [self.create_row(categories="Invalid")]
        sync_prepubs()
        PrepublicationIncident.objects.get(pk=existing_prepub.pk)
        PrepublicationIncidentCategory.objects.get(pk=existing_prepub_category.pk)
