import csv
import datetime
import io
import json

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from wagtail.models import Site

from common.tests.factories import (
    CategoryPageFactory,
    CommonTagFactory,
    PersonPageFactory,
)
from incident import choices
from incident.tests.factories import (
    ChargeFactory,
    ChargeUpdateFactory,
    EquipmentBrokenFactory,
    EquipmentFactory,
    EquipmentSeizedFactory,
    GovernmentWorkerFactory,
    IncidentChargeFactory,
    IncidentChargeWithUpdatesFactory,
    IncidentIndexPageFactory,
    IncidentPageFactory,
    IncidentUpdateFactory,
    InstitutionFactory,
    JournalistFactory,
    LawEnforcementOrganizationFactory,
    LegalOrderFactory,
    LegalOrderUpdateFactory,
    LegalOrderWithUpdatesFactory,
    NationalityFactory,
    PoliticianOrPublicFactory,
    StateFactory,
    TargetedJournalistFactory,
)


class IncidentExportTestCase(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        self.incident_index = IncidentIndexPageFactory.build(slug="incidents")
        root_page.add_child(instance=self.incident_index)

    def test_forbidden_POST(self):
        "POST requests should be forbidden"
        response = self.client.post(self.incident_index.get_full_url() + "export/")
        self.assertEqual(response.status_code, 405)

    def test_OPTIONS(self):
        """
        OPTIONS requests should be allowed and have correct headers but have
        no content
        """

        response = self.client.options(self.incident_index.get_full_url() + "export/")
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response["Access-Control-ALlow-Methods"], "GET,OPTIONS,HEAD")
        self.assertEqual(response.content, b"")

    def test_GET(self):
        """
        OPTIONS requests should be allowed and have correct headers and content
        """

        response = self.client.get(self.incident_index.get_full_url() + "export/")
        self.assertEqual(response["Access-Control-Allow-Origin"], "*")
        self.assertEqual(response["Access-Control-ALlow-Methods"], "GET,OPTIONS,HEAD")

        content = b"".join(list(response.streaming_content)).strip().decode("utf-8")

        # Since we have no incidents in the db right now, this should just be
        # a CSV header row
        headers = set(content.split(","))
        expected_headers = {
            "title",
            "slug",
            "first_published_at",
            "last_published_at",
            "latest_revision_created_at",
            "authors",
            "updates",
            "categories",
            "equipment_seized",
            "equipment_broken",
            "date",
            "exact_date_unknown",
            "city",
            "state",
            "body",
            "introduction",
            "teaser",
            "teaser_image",
            "primary_video",
            "image_caption",
            "arrest_status",
            "arresting_authority",
            "release_date",
            "detention_date",
            "unnecessary_use_of_force",
            "case_number",
            "case_type",
            "case_statuses",
            "status_of_seized_equipment",
            "is_search_warrant_obtained",
            "actor",
            "border_point",
            "target_us_citizenship_status",
            "denial_of_entry",
            "stopped_previously",
            "did_authorities_ask_for_device_access",
            "did_authorities_ask_about_work",
            "assailant",
            "was_journalist_targeted",
            "charged_under_espionage_act",
            "subpoena_type",
            "subpoena_statuses",
            "name_of_business",
            "third_party_business",
            "status_of_prior_restraint",
            "mistakenly_released_materials",
            "targeted_journalists",
            "targeted_institutions",
            "tags",
            "charges",
            "target_nationality",
            "workers_whose_communications_were_obtained",
            "politicians_or_public_figures_involved",
            "type_of_denial",
            "longitude",
            "latitude",
            "legal_orders",
            "legal_order_target",
            "legal_order_venue",
        }
        self.assertEqual(headers, expected_headers)

        # Create incidents
        IncidentPageFactory()
        response = self.client.get(
            self.incident_index.get_full_url() + "export/?format=json"
        )
        response_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0].keys(), expected_headers)

    def test_fields__json(self):
        IncidentPageFactory(
            city="Albuquerque",
            date="2010-01-01",
            title="Took a Wrong Turn",
        )
        response = self.client.get(
            self.incident_index.get_full_url()
            + "export/?format=json&fields=title,city,date"
        )
        response_data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(
            response_data,
            [
                {
                    "city": "Albuquerque",
                    "date": "2010-01-01",
                    "title": "Took a Wrong Turn",
                }
            ],
        )

    def test_fields__csv(self):
        IncidentPageFactory(
            city="Albuquerque",
            date="2010-01-01",
            title="Took a Wrong Turn",
        )
        response = self.client.get(
            self.incident_index.get_full_url()
            + "export/?format=csv&fields=title,city,date"
        )

        content = (
            b"".join(list(response.streaming_content))
            .strip()
            .decode("utf-8")
            .splitlines()
        )
        headers = content[0].split(",")
        data = content[1].split(",")

        expected_headers = ["title", "date", "city"]
        self.assertEqual(headers, expected_headers)

        expected_data = ["Took a Wrong Turn", "2010-01-01", "Albuquerque"]
        self.assertEqual(data, expected_data)


class IncidentExportQueryCountTestCase(TestCase):
    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        self.incident_index = IncidentIndexPageFactory.build(slug="incidents")
        site.root_page.add_child(instance=self.incident_index)
        self.export_url = self.incident_index.get_full_url() + "export/?format=json"

    def create_incident(self):
        incident = IncidentPageFactory(
            journalist_targets=2,
            authors=PersonPageFactory.create_batch(2),
        )
        IncidentChargeWithUpdatesFactory(incident_page=incident)
        LegalOrderWithUpdatesFactory(incident_page=incident)

    def test_query_count_does_not_grow_with_incidents(self):
        # Get the number of queries that a single incident requires on export
        self.create_incident()
        with CaptureQueriesContext(connection) as single:
            self.client.get(self.export_url)

        # Create more incidents and then assert that they use no more queries
        # than the single incident did
        self.create_incident()
        self.create_incident()
        with self.assertNumQueries(len(single)):
            self.client.get(self.export_url)


class IncidentExportRowTestCase(TestCase):
    """Pin the export's column order and the values it writes for an
    incident with every exported column populated."""

    # Column order and values for the incident created in setUp.
    # latitude and longitude are None because IncidentPage.save() derives
    # them from geonames data, which the test database does not have.
    EXPECTED_EXPORT_ROW = [
        ("first_published_at", "2024-01-02 03:04:05+00:00"),
        ("last_published_at", "2024-01-03 03:04:05+00:00"),
        ("title", "Golden incident"),
        ("slug", "http://localhost/incidents/golden-incident/"),
        ("latest_revision_created_at", "2024-01-04 03:04:05+00:00"),
        ("charges", "Charge A (charges pending as of 2024-01-06)"),
        (
            "legal_orders",
            (
                "subpoena for other (unknown as of 2024-01-04), "
                "subpoena for other (pending as of 2024-01-03)"
            ),
        ),
        ("updates", "(2024-01-05 03:04:05+00:00) Update A"),
        ("categories", "Category A"),
        ("equipment_seized", "Camera: count of 2"),
        ("equipment_broken", "Phone: count of 1"),
        ("targeted_journalists", "Journalist A (Institution B)"),
        ("authors", "Author A"),
        ("date", "2024-01-01"),
        ("exact_date_unknown", "False"),
        ("city", "New York"),
        ("state", "New York (NY)"),
        ("latitude", "None"),
        ("longitude", "None"),
        ("body", ""),
        ("introduction", "Introduction text"),
        ("teaser", "Teaser text"),
        ("teaser_image", "None"),
        ("primary_video", "https://example.com/video"),
        ("image_caption", "Image caption"),
        ("arrest_status", "unknown"),
        ("arresting_authority", "New York City Police Department"),
        ("release_date", "2024-01-05"),
        ("detention_date", "2024-01-03"),
        ("unnecessary_use_of_force", "True"),
        ("case_number", "CASE-1"),
        ("case_statuses", "['ONGOING']"),
        ("case_type", "Civil"),
        ("status_of_seized_equipment", "unknown"),
        ("is_search_warrant_obtained", "True"),
        ("actor", "unknown"),
        ("border_point", "JFK International Airport"),
        ("target_us_citizenship_status", "U.S. citizen"),
        ("denial_of_entry", "True"),
        ("stopped_previously", "True"),
        ("did_authorities_ask_for_device_access", "unknown"),
        ("did_authorities_ask_about_work", "unknown"),
        ("assailant", "unknown"),
        ("was_journalist_targeted", "unknown"),
        ("charged_under_espionage_act", "True"),
        ("subpoena_type", "testimony about confidential source"),
        ("subpoena_statuses", "['UNKNOWN']"),
        ("name_of_business", "Megacorp Industries"),
        ("third_party_business", "telecom company"),
        ("legal_order_target", "Journalist"),
        ("legal_order_venue", "State"),
        ("status_of_prior_restraint", "pending"),
        ("mistakenly_released_materials", "True"),
        ("type_of_denial", "['OTHER']"),
        ("targeted_institutions", "Institution A"),
        ("tags", "Tag A"),
        ("target_nationality", "Nationality A"),
        ("workers_whose_communications_were_obtained", "Worker A"),
        ("politicians_or_public_figures_involved", "Politician A"),
    ]

    def setUp(self):
        site = Site.objects.get(is_default_site=True)
        self.incident_index = IncidentIndexPageFactory.build(slug="incidents")
        site.root_page.add_child(instance=self.incident_index)
        self.export_url = self.incident_index.get_full_url() + "export/"

        # Create one incident with as many fields as possible to ensure that
        # export works as expected across all of them.
        published = datetime.datetime(2024, 1, 2, 3, 4, 5, tzinfo=datetime.UTC)
        incident = IncidentPageFactory(
            parent=self.incident_index,
            title="Export incident",
            slug="export-incident",
            first_published_at=published,
            last_published_at=published + datetime.timedelta(days=1),
            latest_revision_created_at=published + datetime.timedelta(days=2),
            date=datetime.date(2024, 1, 1),
            exact_date_unknown=False,
            city="New York",
            state=StateFactory(name="New York", abbreviation="NY"),
            introduction="Introduction text",
            teaser="Teaser text",
            primary_video="https://example.com/video",
            image_caption="Image caption",
            arrest_status=choices.ARREST_STATUS[0][0],
            arresting_authority=LawEnforcementOrganizationFactory(
                title="New York City Police Department"
            ),
            release_date=datetime.date(2024, 1, 5),
            detention_date=datetime.date(2024, 1, 3),
            unnecessary_use_of_force=True,
            case_number="CASE-1",
            case_type=choices.CASE_TYPE[0][0],
            case_statuses=[choices.LegalCaseStatus.ONGOING],
            status_of_seized_equipment=choices.STATUS_OF_SEIZED_EQUIPMENT[0][0],
            is_search_warrant_obtained=True,
            actor=choices.ACTORS[0][0],
            border_point="JFK International Airport",
            target_us_citizenship_status=choices.CITIZENSHIP_STATUS_CHOICES[0][0],
            denial_of_entry=True,
            stopped_previously=True,
            did_authorities_ask_for_device_access=choices.MAYBE_BOOLEAN[0][0],
            did_authorities_ask_about_work=choices.MAYBE_BOOLEAN[0][0],
            assailant=choices.ACTORS[0][0],
            was_journalist_targeted=choices.MAYBE_BOOLEAN[0][0],
            charged_under_espionage_act=True,
            subpoena_type=choices.SUBPOENA_TYPE[0][0],
            subpoena_statuses=[choices.SUBPOENA_STATUS[0][0]],
            name_of_business="Megacorp Industries",
            third_party_business=choices.THIRD_PARTY_BUSINESS[0][0],
            legal_order_target=choices.LegalOrderTarget.JOURNALIST,
            legal_order_venue=choices.LegalOrderVenue.STATE,
            status_of_prior_restraint=choices.STATUS_OF_PRIOR_RESTRAINT[0][0],
            mistakenly_released_materials=True,
            type_of_denial=[choices.TypeOfDenial.OTHER],
            institution_targets=0,
            targeted_institutions=[InstitutionFactory(title="Institution A")],
            authors=[PersonPageFactory(title="Author A")],
            categories=[CategoryPageFactory(title="Category A")],
            tags=[CommonTagFactory(title="Tag A")],
        )
        GovernmentWorkerFactory(title="Worker A").incidents.add(incident)
        NationalityFactory(title="Nationality A").nationality_incidents.add(incident)
        PoliticianOrPublicFactory(
            title="Politician A"
        ).politicians_or_public_incidents.add(incident)
        TargetedJournalistFactory(
            incident=incident,
            journalist=JournalistFactory(title="Journalist A"),
            institution=InstitutionFactory(title="Institution B"),
        )
        IncidentUpdateFactory(
            page=incident,
            title="Update A",
            date=published + datetime.timedelta(days=3),
        )
        EquipmentSeizedFactory(
            incident=incident,
            equipment=EquipmentFactory(name="Camera"),
            quantity=2,
        )
        EquipmentBrokenFactory(
            incident=incident,
            equipment=EquipmentFactory(name="Phone"),
            quantity=1,
        )
        charge = IncidentChargeFactory(
            incident_page=incident,
            charge=ChargeFactory(title="Charge A"),
            date=datetime.date(2024, 1, 3),
            status=choices.STATUS_OF_CHARGES[0][0],
        )
        ChargeUpdateFactory(
            incident_charge=charge,
            date=datetime.date(2024, 1, 4),
            status=choices.STATUS_OF_CHARGES[1][0],
        )
        ChargeUpdateFactory(
            incident_charge=charge,
            date=datetime.date(2024, 1, 6),
            status=choices.STATUS_OF_CHARGES[2][0],
        )
        order = LegalOrderFactory(
            incident_page=incident,
            order_type=choices.LegalOrderType.SUBPOENA,
            information_requested=choices.InformationRequested.OTHER,
            status=choices.LegalOrderStatus.PENDING,
            date=datetime.date(2024, 1, 3),
        )
        LegalOrderUpdateFactory(
            legal_order=order,
            date=datetime.date(2024, 1, 4),
            status=choices.LegalOrderStatus.UNKNOWN,
            sort_order=1,
        )
        LegalOrderFactory(
            incident_page=incident,
            order_type=choices.LegalOrderType.SUBPOENA,
            information_requested=choices.InformationRequested.OTHER,
            status=choices.LegalOrderStatus.PENDING,
            date=datetime.date(2024, 1, 3),
        )

        # Column order and values for the incident
        self.EXPECTED_EXPORT_ROW = [
            ("first_published_at", "2024-01-02 03:04:05+00:00"),
            ("last_published_at", "2024-01-03 03:04:05+00:00"),
            ("title", "Export incident"),
            ("slug", "http://localhost/incidents/export-incident/"),
            ("latest_revision_created_at", "2024-01-04 03:04:05+00:00"),
            ("charges", "Charge A (charges pending as of 2024-01-06)"),
            (
                "legal_orders",
                (
                    "subpoena for other (unknown as of 2024-01-04), "
                    "subpoena for other (pending as of 2024-01-03)"
                ),
            ),
            ("updates", "(2024-01-05 03:04:05+00:00) Update A"),
            ("categories", "Category A"),
            ("equipment_seized", "Camera: count of 2"),
            ("equipment_broken", "Phone: count of 1"),
            ("targeted_journalists", "Journalist A (Institution B)"),
            ("authors", "Author A"),
            ("date", "2024-01-01"),
            ("exact_date_unknown", "False"),
            ("city", "New York"),
            ("state", "New York (NY)"),
            ("latitude", "None"),
            ("longitude", "None"),
            ("body", ""),
            ("introduction", "Introduction text"),
            ("teaser", "Teaser text"),
            ("teaser_image", "None"),
            ("primary_video", "https://example.com/video"),
            ("image_caption", "Image caption"),
            ("arrest_status", "unknown"),
            ("arresting_authority", "New York City Police Department"),
            ("release_date", "2024-01-05"),
            ("detention_date", "2024-01-03"),
            ("unnecessary_use_of_force", "True"),
            ("case_number", "CASE-1"),
            ("case_statuses", "['ONGOING']"),
            ("case_type", "Civil"),
            ("status_of_seized_equipment", "unknown"),
            ("is_search_warrant_obtained", "True"),
            ("actor", "unknown"),
            ("border_point", "JFK International Airport"),
            ("target_us_citizenship_status", "U.S. citizen"),
            ("denial_of_entry", "True"),
            ("stopped_previously", "True"),
            ("did_authorities_ask_for_device_access", "unknown"),
            ("did_authorities_ask_about_work", "unknown"),
            ("assailant", "unknown"),
            ("was_journalist_targeted", "unknown"),
            ("charged_under_espionage_act", "True"),
            ("subpoena_type", "testimony about confidential source"),
            ("subpoena_statuses", "['UNKNOWN']"),
            ("name_of_business", "Megacorp Industries"),
            ("third_party_business", "telecom company"),
            ("legal_order_target", "Journalist"),
            ("legal_order_venue", "State"),
            ("status_of_prior_restraint", "pending"),
            ("mistakenly_released_materials", "True"),
            ("type_of_denial", "['OTHER']"),
            ("targeted_institutions", "Institution A"),
            ("tags", "Tag A"),
            ("target_nationality", "Nationality A"),
            ("workers_whose_communications_were_obtained", "Worker A"),
            ("politicians_or_public_figures_involved", "Politician A"),
        ]

    def test_csv_columns_and_values(self):
        response = self.client.get(self.export_url + "?format=csv")
        content = b"".join(response.streaming_content).decode("utf-8")
        rows = list(csv.reader(io.StringIO(content)))

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], [name for name, _ in self.EXPECTED_EXPORT_ROW])
        self.assertEqual(rows[1], [value for _, value in self.EXPECTED_EXPORT_ROW])

    def test_json_columns_and_values(self):
        response = self.client.get(self.export_url + "?format=json")
        data = json.loads(response.content)

        self.assertEqual(len(data), 1)
        self.assertEqual(list(data[0].items()), self.EXPECTED_EXPORT_ROW)
