from datetime import date

from django.test import TestCase

from .factories import IncidentChargeFactory, IncidentChargeWithUpdatesFactory


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
