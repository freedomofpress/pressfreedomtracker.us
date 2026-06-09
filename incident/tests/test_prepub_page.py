import json
from collections import Counter
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from wagtail.models import Site

from common.models import CategoryPage
from geonames.devdata import create_geoname
from geonames.models import GeoName
from incident.models import (
    IncidentIndexPage,
    IncidentPage,
    PrepublicationIncident,
    PrepublicationIncidentCategory,
    PrepublicationIncidentSync,
    PrepublicationSettings,
)


def create_prepub(
    *,
    date: date = date(2026, 1, 1),
    location: GeoName = None,
    categories: list[CategoryPage] | int = 1,
):

    prepub = PrepublicationIncident.objects.create(
        date=date, location=location or create_geoname()
    )

    match categories:
        case list(category_pages):
            categorizations_to_add = category_pages
        case int(number_to_apply):
            categorizations_to_add = []
            possible_categories = CategoryPage.objects.all().order_by("?")
            if possible_categories:
                categorizations_to_add.extend(possible_categories[:number_to_apply])

    PrepublicationIncidentCategory.objects.bulk_create(
        PrepublicationIncidentCategory(incident=prepub, category=category)
        for category in categorizations_to_add
    )
    return prepub


class PrepubViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)
        cls.category_prior_restraint = CategoryPage(
            title="Test Prior Restraint",
        )
        cls.category_equipment = CategoryPage(
            title="Test Equipment Search/Seizure",
        )
        cls.category_assault = CategoryPage(
            title="Test Assault",
        )
        cls.category_arrest = CategoryPage(
            title="Test Arrest/Criminal Charge",
        )
        site.root_page.add_child(instance=cls.category_prior_restraint)
        site.root_page.add_child(instance=cls.category_equipment)
        site.root_page.add_child(instance=cls.category_assault)
        site.root_page.add_child(instance=cls.category_arrest)
        cls.root_page = site.root_page

        cls.atlanta = create_geoname(name="Atlanta", region="GA")
        cls.baltimore = create_geoname(name="Baltimore", region="MD")
        cls.chicago = create_geoname(name="Chicago", region="IL")
        cls.detroit = create_geoname(name="Detroit", region="MI")

        cls.sync = PrepublicationIncidentSync.objects.create(
            status=PrepublicationIncidentSync.Status.SUCCESS,
        )

        cls.settings = PrepublicationSettings.objects.create(
            timespan_length=1200,
            timespan_units=PrepublicationSettings.TimespanUnits.DAY,
        )

    def test_gets_successfully(self):
        create_prepub(categories=[self.category_equipment])
        response = self.client.get(reverse("prepub_list"))
        self.assertEqual(response.status_code, 200)

    def test_includes_last_updated_time(self):
        response = self.client.get(reverse("prepub_list"))
        time_representation = self.sync.completed_at.strftime("%H:%M %p %Z")
        self.assertContains(response, f"Updated {time_representation}")

    def test_table_groups_rows_by_date_and_location(self):
        create_prepub(
            date=date(2026, 5, 5),
            location=self.atlanta,
            categories=[self.category_equipment],
        )
        create_prepub(
            date=date(2026, 4, 4),
            location=self.atlanta,
            categories=[self.category_equipment],
        )
        create_prepub(
            date=date(2026, 4, 4),
            location=self.atlanta,
            categories=[self.category_assault],
        )
        # Same date as above, different location
        create_prepub(
            date=date(2026, 4, 4),
            location=self.baltimore,
            categories=[self.category_assault],
        )

        # Three incidents, one date & location
        create_prepub(
            date=date(2026, 3, 3),
            location=self.chicago,
            categories=[self.category_assault, self.category_equipment],
        )
        create_prepub(
            date=date(2026, 3, 3),
            location=self.chicago,
            categories=[self.category_assault, self.category_arrest],
        )
        create_prepub(
            date=date(2026, 3, 3),
            location=self.chicago,
            categories=[self.category_arrest, self.category_prior_restraint],
        )

        response = self.client.get(reverse("prepub_list"))
        prepub_rows = response.context["prepubs"]
        self.assertEqual(
            prepub_rows[0],
            {
                "incident_count": 1,
                "date": date(2026, 5, 5),
                "city": "Atlanta",
                "state": "GA",
                "categories": [self.category_equipment.title],
                "category_counts": Counter({self.category_equipment.title: 1}),
            },
        )

        # Incidents grouped by date and location
        self.assertEqual(prepub_rows[1]["incident_count"], 2)
        self.assertEqual(
            prepub_rows[1]["categories"],
            [self.category_equipment.title, self.category_assault.title],
        )
        self.assertEqual(
            {**prepub_rows[1]["category_counts"]},
            {self.category_equipment.title: 1, self.category_assault.title: 1},
        )

        # Three incidents with multiple, overlapping categories each
        self.assertEqual(prepub_rows[3]["incident_count"], 3)
        self.assertEqual(
            {
                # Converting to dict for more readable assertion diffs.
                **prepub_rows[3]["category_counts"]
            },
            {
                self.category_assault.title: 2,
                self.category_arrest.title: 2,
                self.category_equipment.title: 1,
                self.category_prior_restraint.title: 1,
            },
        )

    def test_only_includes_units_in_timespan_of_months(self):
        self.settings.timespan_length = 1
        self.settings.timespan_units = PrepublicationSettings.TimespanUnits.MONTH
        self.settings.save()

        expected = create_prepub(date=date.today())
        create_prepub(date=date.today() - timedelta(days=60))
        response = self.client.get(reverse("prepub_list"))
        prepub_rows = response.context["prepubs"]

        self.assertQuerySetEqual([row["date"] for row in prepub_rows], [expected.date])

    def test_only_includes_units_in_timespan_of_weeks(self):
        self.settings.timespan_length = 1
        self.settings.timespan_units = PrepublicationSettings.TimespanUnits.WEEK
        self.settings.save()

        expected = create_prepub(date=date.today())
        create_prepub(date=date.today() - timedelta(days=8))
        response = self.client.get(reverse("prepub_list"))
        prepub_rows = response.context["prepubs"]

        self.assertEqual([row["date"] for row in prepub_rows], [expected.date])

    def test_only_includes_units_in_timespan_of_days(self):
        self.settings.timespan_length = 2
        self.settings.timespan_units = PrepublicationSettings.TimespanUnits.DAY
        self.settings.save()

        expected = create_prepub(date=date.today())
        create_prepub(date=date.today() - timedelta(days=3))
        response = self.client.get(reverse("prepub_list"))
        prepub_rows = response.context["prepubs"]

        self.assertEqual([row["date"] for row in prepub_rows], [expected.date])

    def test_bar_chart_dataset(self):
        index = self.root_page.add_child(
            instance=IncidentIndexPage(title="All Incidents")
        )

        # Create incident pages for inclusion in the dataset.
        date1 = date.today()
        date2 = date.today() - timedelta(days=1)

        date_old = date.today() - timedelta(days=30)  # Out of bounds for inclusion

        index.add_child(instance=IncidentPage(title="Incident 1", date=date1))
        create_prepub(date=date1)

        index.add_child(instance=IncidentPage(title="Incident 2", date=date2))
        index.add_child(instance=IncidentPage(title="Incident 3", date=date2))
        create_prepub(date=date2)
        create_prepub(date=date2)
        create_prepub(date=date2)

        index.add_child(instance=IncidentPage(title="Incident 4", date=date_old))
        create_prepub(date=date_old)

        response = self.client.get(reverse("prepub_list"))
        bar_chart_dataset = json.loads(response.context["bar_chart_dataset"])

        self.assertEqual(len(bar_chart_dataset), 30)

        # The dataset is ordered by date ascending, so the most recent
        # ones are at the end of the list (hence checking them at
        # index -1, -2, ...)
        for item in bar_chart_dataset[0:-2]:
            self.assertEqual(item["count"], 0)
            self.assertEqual(item["unconfirmed"], 0)
            self.assertEqual(item["confirmed"], 0)

        self.assertEqual(
            bar_chart_dataset[-1],
            {
                "date": f"{date1:%m/%d}",
                "count": 2,
                "confirmed": 1,
                "unconfirmed": 1,
            },
        )

        self.assertEqual(
            bar_chart_dataset[-2],
            {
                "date": f"{date2:%m/%d}",
                "count": 5,
                "confirmed": 2,
                "unconfirmed": 3,
            },
        )
