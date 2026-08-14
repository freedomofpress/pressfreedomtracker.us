import calendar
from datetime import UTC, date, datetime, timedelta
from unittest import mock

from django.test import TestCase

from incident import choices
from incident.devdata import create_prepub
from incident.models import (
    PrepublicationIncident,
    PrepublicationIncidentSync,
    PrepublicationSyncSkippedRow,
)

from .factories import (
    IncidentChargeFactory,
    IncidentChargeWithUpdatesFactory,
    IncidentIndexPageFactory,
    IncidentPageFactory,
    LegalOrderFactory,
    LegalOrderWithUpdatesFactory,
)


class TestLegalOrder(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.legal_order = LegalOrderFactory(
            order_type=choices.LegalOrderType.SUBPOENA,
            information_requested=choices.InformationRequested.TESTIMONY_ABOUT_SOURCE,
            status=choices.LegalOrderStatus.PENDING,
            date="2022-01-01",
        )

        cls.legal_order_with_updates = LegalOrderWithUpdatesFactory(
            order_type=choices.LegalOrderType.SUBPOENA,
            information_requested=choices.InformationRequested.TESTIMONY_ABOUT_SOURCE,
            status=choices.LegalOrderStatus.PENDING,
            date=date(2022, 1, 1),
            update1__status=choices.LegalOrderStatus.UPHELD,
            update2__status=choices.LegalOrderStatus.DROPPED,
            update3__status=choices.LegalOrderStatus.OBJECTED_TO,
            update3__date=date(2022, 2, 2),
        )

    def test_simple_summary(self):
        self.assertEqual(
            self.legal_order.summary,
            "subpoena for testimony about confidential source (pending as of 2022-01-01)",
        )

    def test_summarizes_based_on_most_recent_update_status(self):
        self.assertEqual(
            self.legal_order_with_updates.summary,
            "subpoena for testimony about confidential source (objected to as of 2022-02-02)",
        )

    def test_entries_are_ordered_by_date_ascending(self):
        self.assertEqual(
            self.legal_order_with_updates.entries_display(),
            [
                ("Jan. 1, 2022", "pending"),
                ("Jan. 2, 2022", "upheld"),
                ("Jan. 3, 2022", "dropped"),
                ("Feb. 2, 2022", "objected to"),
            ],
        )


class TestLegalOrderWithUnknownDateUpdate(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.legal_order_with_updates = LegalOrderWithUpdatesFactory(
            order_type=choices.LegalOrderType.SUBPOENA,
            information_requested=choices.InformationRequested.TESTIMONY_ABOUT_SOURCE,
            status=choices.LegalOrderStatus.PENDING,
            date=date(2022, 1, 1),
            update1__status=choices.LegalOrderStatus.UPHELD,
            update2__status=choices.LegalOrderStatus.DROPPED,
            update2__date=None,
            update3__status=choices.LegalOrderStatus.OBJECTED_TO,
            update3__date=None,
        )

    def test_summarizes_based_on_most_recent_update_status(self):
        self.assertEqual(
            self.legal_order_with_updates.summary,
            "subpoena for testimony about confidential source (objected to)",
        )

    def test_entries_are_ordered_by_date_ascending(self):
        self.assertEqual(
            self.legal_order_with_updates.entries_display(),
            [
                ("Jan. 1, 2022", "pending"),
                ("Jan. 2, 2022", "upheld"),
                ("Unknown date", "dropped"),
                ("Unknown date", "objected to"),
            ],
        )


class TestIncidentPageDetentionDuration(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.index = IncidentIndexPageFactory()

    def test_uses_release_date_as_end_date_when_set(self):
        incident = IncidentPageFactory(
            parent=self.index,
            detention_date=date(2020, 1, 1),
            release_date=date(2020, 1, 11),
        )
        self.assertEqual(incident.detention_duration(), timedelta(days=10))

    def test_defaults_to_today_when_no_release_date(self):
        incident = IncidentPageFactory(
            parent=self.index,
            detention_date=date(2020, 1, 1),
            release_date=None,
        )
        with mock.patch(
            "django.utils.timezone.now",
            return_value=datetime(2020, 1, 11, tzinfo=UTC),
        ):
            self.assertEqual(incident.detention_duration(), timedelta(days=10))


class TestIncidentCharge(TestCase):
    def test_simple_summary(self):
        incident_charge = IncidentChargeFactory(
            charge__title="Spying",
            date="2022-01-01",
            status="CHARGES_PENDING",
        )

        self.assertEqual(
            incident_charge.summary, "Spying (charges pending as of 2022-01-01)"
        )

    def test_charges_with_updates(self):
        incident_charge = IncidentChargeWithUpdatesFactory(
            charge__title="Spying",
            date="2019-12-01",
            status="CHARGES_PENDING",
            update1__date="2019-12-02",
            update1__status="NOT_CHARGED",
            update2__date="2019-12-03",
            update2__status="UNKNOWN",
            update3__date="2022-01-02",
            update3__status="ACQUITTED",
        )

        self.assertEqual(incident_charge.summary, "Spying (acquitted as of 2022-01-02)")

    def test_entries_should_be_ordered_by_date_ascending(self):
        incident_charge = IncidentChargeWithUpdatesFactory(
            charge__title="Spying",
            date=date(2019, 12, 2),
            status="CHARGES_PENDING",
            update1__date="2019-12-04",
            update1__status="NOT_CHARGED",
            update2__date="2019-12-13",
            update2__status="UNKNOWN",
            update3__date="2019-12-01",
            update3__status="ACQUITTED",
        )
        self.assertEqual(
            incident_charge.entries_display(),
            [
                ("Dec. 1, 2019", "acquitted"),
                ("Dec. 2, 2019", "charges pending"),
                ("Dec. 4, 2019", "not charged"),
                ("Dec. 13, 2019", "unknown"),
            ],
        )


class TestPrepublicationIncidentQueryset(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.prepub1 = create_prepub(
            date=date(2026, 4, 14),
            date_precision=PrepublicationIncident.DatePrecision.MONTH,
        )
        cls.prepub2 = create_prepub(
            date=date(2025, 1, 1),
            date_precision=PrepublicationIncident.DatePrecision.DAY,
        )
        cls.prepub3 = create_prepub(
            date=date(2025, 3, 1),
            date_precision=33,
        )

    def test_str_method(self):
        self.assertNotIn("14", str(self.prepub1))
        self.assertIn("2025-01-01", str(self.prepub2))
        self.assertIn("33", str(self.prepub3))

    def test_filters_month_precision_dates_by_any_day_in_same_month(self):
        c = calendar.Calendar()
        month = self.prepub1.date.month
        year = self.prepub1.date.year

        for calendar_date in [d for d in c.itermonthdates(year, month)]:
            with self.subTest(calendar_date):
                prepubs_in_range_below = (
                    PrepublicationIncident.objects.fuzzy_date_filter(
                        lower=date(2026, 3, 28),
                        upper=calendar_date,
                    )
                )
                prepubs_in_range_above = (
                    PrepublicationIncident.objects.fuzzy_date_filter(
                        lower=calendar_date,
                        upper=date(2026, 5, 3),
                    )
                )
                if calendar_date < date(2026, 4, 1):
                    self.assertQuerySetEqual(prepubs_in_range_below, [])
                    self.assertQuerySetEqual(prepubs_in_range_above, [self.prepub1])
                elif calendar_date >= date(2026, 5, 1):
                    self.assertQuerySetEqual(prepubs_in_range_below, [self.prepub1])
                    self.assertQuerySetEqual(prepubs_in_range_above, [])
                else:
                    self.assertQuerySetEqual(prepubs_in_range_above, [self.prepub1])
                    self.assertQuerySetEqual(prepubs_in_range_below, [self.prepub1])


class TestPrepublicationIncidentSync(TestCase):
    def setUp(self):
        self.instance = PrepublicationIncidentSync.objects.create(successful_rows=0)

    def test_str_method(self):
        self.assertIn("successful_rows=0", str(self.instance))


class TestPrepublicationSyncSkippedRow(TestCase):
    def setUp(self):
        self.sync = PrepublicationIncidentSync.objects.create()
        self.instance = PrepublicationSyncSkippedRow.objects.create(
            sync=self.sync,
            number=1,
            reason="Invalid",
        )

    def test_str_method(self):
        self.assertIn("number=1", str(self.instance))
        self.assertIn("reason='Invalid'", str(self.instance))
