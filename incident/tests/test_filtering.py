from datetime import date, timedelta
import unittest

from django.test import TestCase
from django.utils import timezone
from wagtail.wagtailcore.rich_text import RichText

from common.tests.factories import CategoryPageFactory
from incident.tests.factories import (
    ChargeFactory,
    IncidentPageFactory,
    IncidentIndexPageFactory,
    InexactDateIncidentPageFactory,
    StateFactory,
    TargetFactory,
)
from incident.utils.incident_filter import IncidentFilter


class TestFiltering(TestCase):
    """Incident filters"""
    def setUp(self):
        self.index = IncidentIndexPageFactory()

    def test_should_filter_by_search_text(self):
        """should filter by search text."""
        incident1 = IncidentPageFactory(
            body__0__rich_text__value=RichText('eggplant'),
        )
        IncidentPageFactory(
            body__0__rich_text__value=RichText('science fiction'),
        )

        incidents = IncidentFilter(dict(
            search='eggplant',
        )).get_queryset()

        self.assertEqual({incident1}, set(incidents))

    def test_should_filter_by_category(self):
        """should filter by category."""
        category1 = CategoryPageFactory()
        category2 = CategoryPageFactory()
        incident1 = IncidentPageFactory(categories=[category1])
        IncidentPageFactory(title='Not relevant', categories=[category2])

        incidents = IncidentFilter(dict(
            categories=str(category1.id),
        )).get_queryset()
        self.assertEqual(set(incidents), {incident1})

    def test_should_filter_by_any_category_given(self):
        """should filter by multiple categories."""
        category1 = CategoryPageFactory()
        category2 = CategoryPageFactory()
        category3 = CategoryPageFactory()
        incident1 = IncidentPageFactory(categories=[category1, category3])
        incident2 = IncidentPageFactory(categories=[category2])

        incidents = IncidentFilter(dict(
            categories='{0},{1}'.format(str(category2.id), str(category3.id)),
        )).get_queryset()
        self.assertEqual({incident1, incident2}, set(incidents))

    def test_should_filter_by_char_field(self):
        """should filter via a field that is a char field"""
        affiliation = 'cauliflower'
        target = IncidentPageFactory(
            affiliation=affiliation,
        )
        IncidentPageFactory(
            affiliation='other'
        )
        incidents = IncidentFilter(dict(
            affiliation=affiliation
        )).get_queryset()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_circuit(self):
        # See incident/circuits.py
        circuit = 'eleventh'
        alabama = StateFactory(name='Alabama')
        florida = StateFactory(name='Florida')
        alaska = StateFactory(name='Alaska')
        target1 = IncidentPageFactory(state=alabama, title='Alabama')
        target2 = IncidentPageFactory(state=florida, title='Florida')
        IncidentPageFactory(state=alaska, title='Alaska')

        incidents = IncidentFilter(dict(
            circuits=circuit,
        )).get_queryset()

        self.assertEqual(set(incidents), {target1, target2})

    def test_should_filter_charges_as_one_field(self):
        """Filter should filter charges as if current and dropped charges are a single field"""
        category = CategoryPageFactory(
            title='Arrest / Criminal Charge',
            incident_filters=['charges'],
        )
        charge = ChargeFactory()
        target1 = IncidentPageFactory(categories=[category])
        target2 = IncidentPageFactory(categories=[category])
        IncidentPageFactory(categories=[category])

        target1.current_charges.add(charge)
        target2.dropped_charges.add(charge)
        target1.current_charges.commit()
        target2.dropped_charges.commit()

        incidents = IncidentFilter(dict(
            categories=str(category.id),
            charges=str(charge.pk),
        )).get_queryset()

        self.assertEqual(set(incidents), {target1, target2})


class TestBooleanFiltering(TestCase):
    """Boolean filters"""
    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryPageFactory(
            title='Leak Case',
            incident_filters=['charged_under_espionage_act'],
        )

        cls.true_bool = IncidentPageFactory(
            categories=[cls.category],
            charged_under_espionage_act=True
        )
        cls.false_bool = IncidentPageFactory(
            categories=[cls.category],
            charged_under_espionage_act=False
        )

    def test_should_filter_by_true_boolean_field(self):
        """should filter by boolean when true"""
        incidents = IncidentFilter(dict(
            charged_under_espionage_act='True',
            categories=str(self.category.id),
        )).get_queryset()

        self.assertEqual(set(incidents), {self.true_bool})

    def test_should_filter_by_false_boolean_field(self):
        """should filter by boolean when false"""
        incidents = IncidentFilter(dict(
            charged_under_espionage_act='False',
            categories=str(self.category.id),
        )).get_queryset()

        self.assertEqual(set(incidents), {self.false_bool})

    def test_should_return_all_with_invalid_bool(self):
        """Should return all incidents when filter is invalid"""
        incidents = IncidentFilter(dict(
            charged_under_espionage_act='Hello',
            categories=str(self.category.id),
        )).get_queryset()

        self.assertEqual(set(incidents), {self.true_bool, self.false_bool})

    def test_should_return_all_with_none_bool(self):
        incidents = IncidentFilter({
            'categories': str(self.category.id),
        }).get_queryset()

        self.assertEqual(set(incidents), {self.true_bool, self.false_bool})


class TestAllFiltersAtOnce(TestCase):
    def test_all_filters_combined_with_search(self):
        """filters should be searchable

        This tests will raise an error if any fields given to
        IncidentFilter are not configured as `search_fields` on
        IncidentPage.

        """
        available_filters = IncidentFilter.get_available_filters()

        # get a valid value for a given field
        def value_for_field(field):
            t = field['type']
            if t == 'text':
                return 'value'
            elif t == 'pk' or t == 'autocomplete':
                return '1'
            elif t == 'choice' or t == 'radio':
                filter_ = available_filters[field['name']]
                return list(filter_.get_choices())[0]
            elif t == 'bool':
                return 'True'
            else:
                raise ValueError('Could not determine value for field of type %s' % t)

        category = CategoryPageFactory(incident_filters=available_filters)

        # skip these fields directly because they are split into
        # upper_date and lower_date fields, and because we pass
        # an explicit categories value
        filters_to_skip = {'date', 'detention_date', 'release_date', 'categories'}
        incident_filter = IncidentFilter(dict(
            search='search text',
            date_lower='2011-01-01',
            date_upper='2012-01-01',
            categories=str(category.id),
            release_date_lower='2011-01-01',
            release_date_upper='2012-01-01',
            detention_date_lower='2011-01-01',
            detention_date_upper='2012-01-01',
            **{
                available_filters[obj.incident_filter].name: value_for_field(available_filters[obj.incident_filter].serialize())
                for obj in category.incident_filters.all()
                if available_filters[obj.incident_filter].name not in filters_to_skip
            }
        ))
        # This test passes if the following functions complete with no
        # errors.
        incident_filter.clean(strict=True)
        incident_filter.get_queryset()
        incident_filter.get_summary()

        self.assertEqual(
            set(incident_filter.cleaned_data),
            {
                filter_name
                for filter_name in IncidentFilter.get_available_filters()
                if filter_name not in filters_to_skip
            } | {
                'date',
                'detention_date',
                'release_date',
                'search',
                'categories',
            }
        )


class FuzzyDateFilterTest(TestCase):
    def test_should_filter_by_date_range(self):
        """should filter by date range."""
        target = IncidentPageFactory(date=date(2017, 1, 15))
        IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 2, 1))

        incidents = IncidentFilter(dict(
            date_upper='2017-01-31',
            date_lower='2017-01-01',
        )).get_queryset()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_filter_by_date_range_should_be_inclusive_on_upper_date(self):
        """date filter should include incidents that occur on the upper date"""
        target_date = date(2017, 2, 12)
        target = IncidentPageFactory(date=target_date)
        IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 4, 1))

        incidents = IncidentFilter(dict(
            date_upper=target_date.isoformat(),
            date_lower='2017-01-01',
        )).get_queryset()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_date_range_unbounded_below(self):
        """should filter by date range - unbounded below."""
        incident1 = IncidentPageFactory(date=date(2017, 1, 15))
        incident2 = IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 2, 1))

        incidents = IncidentFilter(dict(
            date_upper='2017-01-31',
        )).get_queryset()

        self.assertEqual({incident2, incident1}, set(incidents))

    def test_should_find_inexactly_dated_incidents_from_above(self):
        """should locate inexactly dated incidents if filter date range
begins in the same month"""
        # InexactDateIncidentPageFactory creates pages in 2017-03
        targets = InexactDateIncidentPageFactory.create_batch(15)
        incidents = IncidentFilter(dict(
            date_lower='2017-03-15',
            date_upper='2017-04-15',
        )).get_queryset()
        for target in targets:
            self.assertIn(target, incidents)
        self.assertEqual(len(incidents), 15)

    def test_should_find_inexactly_dated_incidents_from_below(self):
        """should locate inexactly dated incidents if filter date range ends anytime in the same month"""
        # InexactDateIncidentPageFactory creates pages in 2017-03
        targets = InexactDateIncidentPageFactory.create_batch(15)

        incidents = IncidentFilter(dict(
            date_lower='2017-02-20',
            date_upper='2017-03-03',
        )).get_queryset()

        for target in targets:
            self.assertIn(target, incidents)
        self.assertEqual(len(incidents), 15)

    def test_should_not_include_inexactly_dated_incidents_from_other_months__below(self):
        """should not include inexactly dated incidents if filter date range
excludes all dates from the same month"""
        # InexactDateIncidentPageFactory creates pages in 2017-03
        InexactDateIncidentPageFactory.create_batch(15)

        incidents = IncidentFilter(dict(
            date_lower='2017-02-02',
            date_upper='2017-02-28',
        )).get_queryset()
        self.assertEqual(len(incidents), 0)

    @unittest.skip('Test currently fails on master as well; leaving for another ticket')
    def test_should_not_include_inexactly_dated_incidents_from_other_months__above(self):
        """should not include inexactly dated incidents if filter date range
excludes all dates from the same month"""
        # InexactDateIncidentPageFactory creates pages in 2017-03
        InexactDateIncidentPageFactory.create_batch(15)

        incident_filter = IncidentFilter(dict(
            date_lower='2017-04-01',
            date_upper='2017-04-15',
        ))
        incidents = incident_filter.get_queryset()
        self.assertEqual(incident_filter.cleaned_data, {'date': (date(2017, 4, 1), date(2017, 4, 15))})
        self.assertEqual(len(incidents), 0)

    def test_should_filter_by_date_range_unbounded_above(self):
        """should filter by date range - unbounded above"""
        incident1 = IncidentPageFactory(date=date(2017, 1, 15))
        IncidentPageFactory(date=date(2016, 12, 31))
        incident2 = IncidentPageFactory(date=date(2017, 2, 1))

        incidents = IncidentFilter(dict(
            date_lower='2017-01-01',
        )).get_queryset()

        self.assertEqual({incident2, incident1}, set(incidents))


class DateFilterTest(TestCase):
    """Date filters"""
    @classmethod
    def setUpTestData(cls):
        cls.category = CategoryPageFactory(
            title='Arrest / Criminal Charge',
            incident_filters=['release_date'],
        )

    def setUp(self):
        self.date_lower = date(2017, 2, 12)
        self.date_upper = date(2017, 2, 13)

    def test_should_filter_by_date_lower_inclusive(self):
        """should filter by lower date"""
        target = IncidentPageFactory(
            release_date=self.date_lower,
            categories=[self.category],
        )

        # This incident should not be included in the filter, because it is before the lower date
        IncidentPageFactory(
            release_date=(self.date_lower - timedelta(days=1)),
            categories=[self.category],
        )

        incidents = IncidentFilter(dict(
            release_date_lower=self.date_lower.isoformat(),
            categories=str(self.category.id),
        )).get_queryset()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_date_upper_inclusive(self):
        """should filter by upper date"""
        target = IncidentPageFactory(
            release_date=self.date_upper,
            categories=[self.category],
        )

        # This incident should not be included in the filter, because it is after the upper date
        IncidentPageFactory(
            release_date=(self.date_upper + timedelta(days=1)),
            categories=[self.category],
        )

        incidents = IncidentFilter(dict(
            release_date_upper=self.date_upper.isoformat(),
            categories=str(self.category.id),
        )).get_queryset()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_date_range_inclusive(self):
        """should filter by date range"""
        target1 = IncidentPageFactory(
            release_date=self.date_lower,
            categories=[self.category],
        )

        target2 = IncidentPageFactory(
            release_date=self.date_upper,
            categories=[self.category],
        )

        # Incidents below and above the filters
        IncidentPageFactory(
            release_date=(self.date_lower - timedelta(days=1)),
            categories=[self.category],
        )
        IncidentPageFactory(
            release_date=(self.date_upper + timedelta(days=1)),
            categories=[self.category],
        )

        incidents = IncidentFilter(dict(
            release_date_lower=self.date_lower.isoformat(),
            release_date_upper=self.date_upper.isoformat(),
            categories=str(self.category.id),
        )).get_queryset()

        self.assertEqual(len(incidents), 2)
        self.assertTrue(target1 in incidents)
        self.assertTrue(target2 in incidents)

    def test_should_filter_correctly_with_equal_dates(self):
        """should filter correctly if upper and lower dates are equal"""
        target = IncidentPageFactory(
            release_date=self.date_lower,
            categories=[self.category],
        )

        # This incident should not be included in the filer, because it is before the lower date
        IncidentPageFactory(
            release_date=(self.date_lower - timedelta(days=1)),
            categories=[self.category],
        )
        IncidentPageFactory(
            release_date=(self.date_lower + timedelta(days=1)),
            categories=[self.category],
        )

        incidents = IncidentFilter(dict(
            release_date_lower=self.date_lower.isoformat(),
            release_date_upper=self.date_lower.isoformat(),
            categories=str(self.category.id),
        )).get_queryset()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_end_of_year_queries_succeed(self):
        """
        Queries made at the end of the year should not look up nonexistent
        month 13.
        """
        incident1 = IncidentPageFactory(
            date=date(2017, 12, 1),
            categories=[self.category],
        )
        incident2 = IncidentPageFactory(
            date=date(2017, 12, 2),
            categories=[self.category],
        )

        incidents = IncidentFilter(dict(
            date_upper='2017-12-31',
            categories=str(self.category.id),
        )).get_queryset()

        self.assertEqual({incident1, incident2}, set(incidents))

    def test_nearly_end_of_year_queries_succeed(self):
        """
        Queries made at near the end of year should not fail. This test complements
        the `end_of_year_queries_succeed` test, to provide additional debugging data
        if one succeeds and the other does not.
        """
        incident1 = IncidentPageFactory(
            date=date(2017, 11, 1),
            categories=[self.category],
        )
        incident2 = IncidentPageFactory(
            date=date(2017, 11, 2),
            categories=[self.category],
        )

        incidents = IncidentFilter(dict(
            date_upper='2017-11-31',
            categories=str(self.category.id),
        )).get_queryset()

        self.assertEqual({incident1, incident2}, set(incidents))


class ChoiceFilterTest(TestCase):
    def setUp(self):
        self.custody = 'CUSTODY'
        self.returned_full = 'RETURNED_FULL'
        self.unknown = 'UNKNOWN'
        self.category = CategoryPageFactory(
            title='Equipment Search or Seizure',
            incident_filters=['status_of_seized_equipment'],
        )

    def test_should_filter_by_choice_field(self):
        """should filter via a field that is a choice field"""

        target = IncidentPageFactory(
            status_of_seized_equipment=self.custody,
            categories=[self.category],
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.returned_full,
            categories=[self.category],
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            status_of_seized_equipment=self.custody,
        ))

        incidents = incident_filter.get_queryset()
        self.assertEqual(incidents.count(), 1)
        self.assertIn(target, incidents)
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': [self.category.id],
            'status_of_seized_equipment': [self.custody],
        })

    def test_filter_should_return_all_if_choice_field_invalid(self):
        """should not filter if choice is invalid"""

        IncidentPageFactory(
            status_of_seized_equipment=self.custody,
            categories=[self.category],
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.returned_full,
            categories=[self.category],
        )
        IncidentPageFactory(
            affiliation='other',
            categories=[self.category],
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            status_of_seized_equipment="hello",
        ))

        incidents = incident_filter.get_queryset()
        self.assertEqual(incidents.count(), 3)
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': [self.category.id],
        })

    def test_filter_should_handle_multiple_choices(self):
        """should handle multiple choices"""
        target1 = IncidentPageFactory(
            status_of_seized_equipment=self.custody,
            categories=[self.category],
        )
        target2 = IncidentPageFactory(
            status_of_seized_equipment=self.returned_full,
            categories=[self.category],
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.unknown,
            categories=[self.category],
        )

        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            status_of_seized_equipment='{0},{1}'.format(self.custody, self.returned_full),
        ))

        incidents = incident_filter.get_queryset()
        self.assertEqual(incidents.count(), 2)
        self.assertIn(target1, incidents)
        self.assertIn(target2, incidents)
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': [self.category.id],
            'status_of_seized_equipment': [self.custody, self.returned_full],
        })


class GetSummaryTest(TestCase):
    def setUp(self):
        self.custody = 'CUSTODY'
        self.returned_full = 'RETURNED_FULL'
        self.category = CategoryPageFactory(
            title='Equipment Search or Seizure',
            incident_filters=['status_of_seized_equipment'],
        )

    def test_single_category_excludes_category_count(self):
        IncidentPageFactory(
            status_of_seized_equipment=self.custody,
            categories=[self.category],
            date=timezone.now().date(),
            targets=0,
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.returned_full,
            categories=[self.category],
            date=timezone.now().date(),
            targets=0,
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            status_of_seized_equipment=self.custody,
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 1),
            ('Journalists affected', 0),
            ('Results in {}'.format(timezone.now().year), 1),
            ('Results in {0:%B}'.format(timezone.now().date()), 1),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': [self.category.id],
            'status_of_seized_equipment': [self.custody],
        })

    def test_category_incident_count_filtered(self):
        category2 = CategoryPageFactory(
            title='Other category',
        )
        IncidentPageFactory(
            lawsuit_name='Lawsuit One',
            categories=[self.category],
            date=timezone.now().date(),
            targets=0,
        )
        IncidentPageFactory(
            lawsuit_name='Lawsuit Two',
            categories=[self.category],
            date=timezone.now().date(),
            targets=0,
        )
        IncidentPageFactory(
            lawsuit_name='Lawsuit One',
            categories=[category2],
            date=timezone.now().date(),
            targets=0,
        )
        incident_filter = IncidentFilter(dict(
            categories='{},{}'.format(self.category.id, category2.id),
            lawsuit_name='Lawsuit One',
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 2),
            ('Journalists affected', 0),
            ('Results in {}'.format(timezone.now().year), 2),
            ('Results in {0:%B}'.format(timezone.now().date()), 2),
            (self.category.title, 1),
            (category2.title, 1),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': [self.category.id, category2.id],
            'lawsuit_name': 'Lawsuit One',
        })

    def test_target_count__filtered(self):
        # Matched incident page
        IncidentPageFactory(
            status_of_seized_equipment=self.custody,
            categories=[self.category],
            date=timezone.now().date(),
            targets=3,
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.returned_full,
            categories=[self.category],
            date=timezone.now().date(),
            targets=5,
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            status_of_seized_equipment=self.custody,
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 1),
            ('Journalists affected', 3),
            ('Results in {}'.format(timezone.now().year), 1),
            ('Results in {0:%B}'.format(timezone.now().date()), 1),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': [self.category.id],
            'status_of_seized_equipment': [self.custody],
        })

    def test_target_count__combined(self):
        IncidentPageFactory(
            categories=[self.category],
            date=timezone.now().date(),
            targets=3,
        )
        IncidentPageFactory(
            categories=[self.category],
            date=timezone.now().date(),
            targets=5,
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 2),
            ('Journalists affected', 8),
            ('Results in {}'.format(timezone.now().year), 2),
            ('Results in {0:%B}'.format(timezone.now().date()), 2),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': [self.category.id],
        })

    def test_target_count__deduped(self):
        target1 = TargetFactory()
        target2 = TargetFactory()
        incident1 = IncidentPageFactory(
            categories=[self.category],
            date=timezone.now().date(),
            targets=0,
        )
        incident1.targets = [target1, target2]
        incident1.save()

        incident2 = IncidentPageFactory(
            categories=[self.category],
            date=timezone.now().date(),
            targets=0,
        )
        incident2.targets = [target1]
        incident2.save()

        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 2),
            ('Journalists affected', 2),
            ('Results in {}'.format(timezone.now().year), 2),
            ('Results in {0:%B}'.format(timezone.now().date()), 2),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': [self.category.id],
        })
