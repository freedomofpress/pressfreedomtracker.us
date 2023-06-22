from datetime import date

from django.test import TestCase

from incident import choices
from .factories import (
    IncidentChargeFactory,
    IncidentChargeWithUpdatesFactory,
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
            date='2022-01-01',
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
            'subpoena for testimony about confidential source (pending as of 2022-01-01)'
        )

    def test_summarizes_based_on_most_recent_update_status(self):
        self.assertEqual(
            self.legal_order_with_updates.summary,
            'subpoena for testimony about confidential source (objected to as of 2022-02-02)'
        )

    def test_entries_are_ordered_by_date_ascending(self):
        self.assertEqual(
            self.legal_order_with_updates.entries_display(),
            [
                ('Jan. 1, 2022', 'pending'),
                ('Jan. 2, 2022', 'upheld'),
                ('Jan. 3, 2022', 'dropped'),
                ('Feb. 2, 2022', 'objected to'),
            ]
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
            'subpoena for testimony about confidential source (objected to)'
        )

    def test_entries_are_ordered_by_date_ascending(self):
        self.assertEqual(
            self.legal_order_with_updates.entries_display(),
            [
                ('Jan. 1, 2022', 'pending'),
                ('Jan. 2, 2022', 'upheld'),
                ('Unknown date', 'dropped'),
                ('Unknown date', 'objected to'),
            ]
        )


class TestIncidentCharge(TestCase):
    def test_simple_summary(self):
        incident_charge = IncidentChargeFactory(
            charge__title='Spying',
            date='2022-01-01',
            status='CHARGES_PENDING',
        )

        self.assertEqual(
            incident_charge.summary,
            'Spying (charges pending as of 2022-01-01)'
        )

    def test_charges_with_updates(self):
        incident_charge = IncidentChargeWithUpdatesFactory(
            charge__title='Spying',
            date='2019-12-01',
            status='CHARGES_PENDING',
            update1__date='2019-12-02',
            update1__status='NOT_CHARGED',
            update2__date='2019-12-03',
            update2__status='UNKNOWN',
            update3__date='2022-01-02',
            update3__status='ACQUITTED',
        )

        self.assertEqual(
            incident_charge.summary,
            'Spying (acquitted as of 2022-01-02)'
        )

    def test_entries_should_be_ordered_by_date_ascending(self):
        incident_charge = IncidentChargeWithUpdatesFactory(
            charge__title='Spying',
            date=date(2019, 12, 2),
            status='CHARGES_PENDING',
            update1__date='2019-12-04',
            update1__status='NOT_CHARGED',
            update2__date='2019-12-13',
            update2__status='UNKNOWN',
            update3__date='2019-12-01',
            update3__status='ACQUITTED',
        )
        self.assertEqual(
            incident_charge.entries_display(),
            [
                ('Dec. 1, 2019', 'acquitted'),
                ('Dec. 2, 2019', 'charges pending'),
                ('Dec. 4, 2019', 'not charged'),
                ('Dec. 13, 2019', 'unknown'),
            ]
        )
