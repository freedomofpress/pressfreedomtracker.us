from itertools import chain
from datetime import date, timedelta

from django.test import TestCase
from wagtail.wagtailcore.rich_text import RichText

from incident.tests.factories import (
    IncidentPageFactory,
    IncidentIndexPageFactory,
    IncidentCategorizationFactory,
    InexactDateIncidentPageFactory,
    StateFactory,
)
from common.tests.factories import CategoryPageFactory
from incident.utils.incident_filter import IncidentFilter
from incident.utils.incident_fields import (
    INCIDENT_PAGE_FIELDS,
    ARREST_FIELDS,
    LAWSUIT_FIELDS,
    EQUIPMENT_FIELDS,
    BORDER_STOP_FIELDS,
    PHYSICAL_ASSAULT_FIELDS,
    SUBPOENA_FIELDS,
    LEAK_PROSECUTIONS_FIELDS,
    LEGAL_ORDER_FIELDS,
    PRIOR_RESTRAINT_FIELDS,
    DENIAL_OF_ACCESS_FIELDS
)

from incident.circuits import CIRCUITS_BY_STATE
from incident.tests.utils import create_incident_filter


class TestFiltering(TestCase):
    """Incident filters"""
    def setUp(self):
        self.index = IncidentIndexPageFactory()

    def test_should_filter_by_date_range(self):
        """should filter by date range."""
        target = IncidentPageFactory(date=date(2017, 1, 15))
        IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 2, 1))

        summary, incidents = create_incident_filter(
            date_upper='2017-01-31',
            date_lower='2017-01-01',
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_filter_by_date_range_should_be_incluve_on_upper_date(self):
        """date filter should include incidents that occur on the upper date"""
        target_date = date(2017, 2, 12)
        target = IncidentPageFactory(date=target_date)
        IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 4, 1))

        summary, incidents = create_incident_filter(
            date_upper=target_date.isoformat(),
            date_lower='2017-01-01',
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_date_range_unbounded_below(self):
        """should filter by date range - unbounded below."""
        incident1 = IncidentPageFactory(date=date(2017, 1, 15))
        incident2 = IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 2, 1))

        summary, incidents = create_incident_filter(
            date_upper='2017-01-31',
        ).fetch()

        self.assertEqual({incident2, incident1}, set(incidents))

    def test_should_find_inexactly_dated_incidents_2(self):
        """should locate inexactly dated incidents if filter date range
begins in the same month"""
        targets = InexactDateIncidentPageFactory.create_batch(15)
        _, incidents = create_incident_filter(
            lower_date='2017-03-15',
            upper_date='2017-04-15',
        ).fetch()
        for target in targets:
            self.assertIn(target, incidents)
        self.assertEqual(len(incidents), 15)

    def test_should_find_inexactly_dated_incidents_from_below(self):
        """should locate inexactly dated incidents if filter date range ends anytime in the same month"""
        targets = InexactDateIncidentPageFactory.create_batch(15)

        _, incidents = create_incident_filter(
            lower_date='2017-02-20',
            upper_date='2017-03-03',
        ).fetch()

        for target in targets:
            self.assertIn(target, incidents)
        self.assertEqual(len(incidents), 15)

    def test_should_find_inexactly_dated_incidents_from_above(self):
        """should locate inexactly dated incidents if filter date range
includes any dates from the same month"""
        targets = InexactDateIncidentPageFactory.create_batch(15)

        _, incidents = create_incident_filter(
            lower_date='2017-02-20',
            upper_date='2017-03-03',
        ).fetch()

        for target in targets:
            self.assertIn(target, incidents)
        self.assertEqual(len(incidents), 15)

    def test_should_not_include_inexactly_dated_incidents_from_other_months(self):
        """should not include inexactly dated incidents if filter date range
excludes all dates from the same month"""
        InexactDateIncidentPageFactory.create_batch(15)

        _, incidents = create_incident_filter(
            date_lower='2017-02-02',
            date_upper='2017-02-28',
        ).fetch()
        self.assertEqual(len(incidents), 0)

    def test_should_filter_by_date_range_unbounded_above(self):
        """should filter by date range - unbounded above"""
        incident1 = IncidentPageFactory(date=date(2017, 1, 15))
        IncidentPageFactory(date=date(2016, 12, 31))
        incident2 = IncidentPageFactory(date=date(2017, 2, 1))

        summary, incidents = create_incident_filter(
            date_lower='2017-01-01',
        ).fetch()

        self.assertEqual({incident2, incident1}, set(incidents))

    def test_should_filter_by_search_text(self):
        """should filter by search text."""
        incident1 = IncidentPageFactory(
            body__0__rich_text__value=RichText('eggplant'),
        )
        IncidentPageFactory(
            body__0__rich_text__value=RichText('science fiction'),
        )

        summary, incidents = create_incident_filter(
            search_text='eggplant',
        ).fetch()

        self.assertEqual({incident1}, set(incidents))

    def test_should_filter_by_category(self):
        """should filter by category."""
        category1 = CategoryPageFactory()
        category2 = CategoryPageFactory()
        incident1 = IncidentPageFactory()
        not_relevant = IncidentPageFactory(title='Not relevant')

        ic1 = IncidentCategorizationFactory.create(
            category=category1,
            incident_page=incident1
        )
        ic1.save()
        ic2 = IncidentCategorizationFactory(
            category=category2,
            incident_page=not_relevant,
        )
        ic2.save()

        summary, incidents = create_incident_filter(
            categories=str(category1.id),
        ).fetch()
        self.assertEqual({incident1}, set(incidents))

    def test_should_filter_by_any_category_given(self):
        """should filter by multiple categories."""
        category1 = CategoryPageFactory()
        category2 = CategoryPageFactory()
        category3 = CategoryPageFactory()
        incident1 = IncidentPageFactory()
        incident2 = IncidentPageFactory(title='Not relevant')

        ic1 = IncidentCategorizationFactory.create(
            category=category1,
            incident_page=incident1
        )
        ic1.save()
        ic2 = IncidentCategorizationFactory(
            category=category2,
            incident_page=incident2,
        )
        ic2.save()
        ic3 = IncidentCategorizationFactory.create(
            category=category3,
            incident_page=incident1,
        )
        ic3.save()

        summary, incidents = create_incident_filter(
            categories='{0},{1}'.format(str(category2.id), str(category3.id)),
        ).fetch()
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
        summary, incidents = create_incident_filter(
            affiliation=affiliation
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_circuit(self):
        state = StateFactory()
        circuit = CIRCUITS_BY_STATE[state.name]
        target = IncidentPageFactory(state=state)

        summary, incidents = create_incident_filter(
            circuit=circuit
        ).fetch()

        self.assertTrue(target in incidents)
        self.assertEqual(len(incidents), 1)


class TestBooleanFiltering(TestCase):
    """Boolean filters"""
    def setUp(self):
        category = CategoryPageFactory(slug='leak-prosecutions')
        category.save()

        self.true_bool = IncidentPageFactory(
            charged_under_espionage_act=True
        )
        self.false_bool = IncidentPageFactory(
            charged_under_espionage_act=False
        )

        tc = IncidentCategorizationFactory.create(
            category=category,
            incident_page=self.true_bool,
        )
        tc.save()

        oc = IncidentCategorizationFactory.create(
            category=category,
            incident_page=self.false_bool,
        )
        oc.save()

    def test_should_filter_by_true_boolean_field(self):
        """should filter by boolean when true"""
        summary, incidents = create_incident_filter(
            charged_under_espionage_act='True'
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(self.true_bool in incidents)

    def test_should_filter_by_false_boolean_field(self):
        """should filter by boolean when false"""
        summary, incidents = create_incident_filter(
            charged_under_espionage_act='False'
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(self.false_bool in incidents)

    def test_should_return_all_with_invalid_bool(self):
        """Should return all incidents when filter is invalid"""
        summary, incidents = create_incident_filter(
            charged_under_espionage_act='Hello'
        ).fetch()

        self.assertEqual(len(incidents), 2)


class TestAllFiltersAtOnce(TestCase):
    def test_all_filters_combined_with_search(self):
        """filters should be searchable

        This tests will raise an error if any fields given to
        IncidentFilter are not configured as `search_fields` on
        IncidentPage.

        """
        # skip these fields directly because they are split into
        # upper_date and lower_date fields
        fields_to_skip = {'date', 'detention_date', 'release_date'}

        # get a valid value for a given field
        def value_for_field(field):
            t = field['type']
            if t == 'char':
                return 'value'
            elif t == 'pk':
                return '1'
            elif t == 'choice':
                return field['choices'][0][0]
            elif t == 'bool':
                return 'True'
            else:
                raise ValueError('Could not determine value for field of type %s' % t)

        filters = IncidentFilter(
            search_text='search text',
            date_lower='2011-01-01',
            date_upper='2012-01-01',
            categories='1',
            circuits='first',
            release_date_upper='2011-01-01',
            release_date_lower='2012-01-01',
            detention_date_upper='2011-01-01',
            detention_date_lower='2012-01-01',
            **{f['name']: value_for_field(f) for f in chain(
                INCIDENT_PAGE_FIELDS,
                ARREST_FIELDS,
                LAWSUIT_FIELDS,
                EQUIPMENT_FIELDS,
                BORDER_STOP_FIELDS,
                PHYSICAL_ASSAULT_FIELDS,
                SUBPOENA_FIELDS,
                LEAK_PROSECUTIONS_FIELDS,
                LEGAL_ORDER_FIELDS,
                PRIOR_RESTRAINT_FIELDS,
                DENIAL_OF_ACCESS_FIELDS
            ) if f['name'] not in fields_to_skip
            })
        # This test passes if the following function completes with no
        # errors.
        filters.fetch()


class TestDateFilters(TestCase):
    """Date filters"""
    def setUp(self):
        self.date_lower = date(2017, 2, 12)
        self.date_upper = date(2017, 2, 13)

    def test_should_filter_by_date_lower_inclusive(self):
        """should filter by lower date"""
        target = IncidentPageFactory(
            release_date=self.date_lower
        )

        # This incident should not be included in the filer, because it is before the lower date
        IncidentPageFactory(
            release_date=(self.date_lower - timedelta(days=1))
        )

        summary, incidents = create_incident_filter(
            release_date_lower=self.date_lower.isoformat()
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_date_upper_inclusive(self):
        """should filter by upper date"""
        target = IncidentPageFactory(
            release_date=self.date_upper
        )

        # This incident should not be included in the filer, because it is after the upper date
        IncidentPageFactory(
            release_date=(self.date_upper + timedelta(days=1))
        )

        summary, incidents = create_incident_filter(
            release_date_upper=self.date_upper.isoformat()
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_date_range_inclusive(self):
        """should filter by date range"""
        target1 = IncidentPageFactory(
            release_date=self.date_upper
        )

        target2 = IncidentPageFactory(
            release_date=(self.date_upper)
        )

        # Incidents below and above the filters
        IncidentPageFactory(
            release_date=(self.date_lower - timedelta(days=1))
        )
        IncidentPageFactory(
            release_date=(self.date_upper + timedelta(days=1))
        )

        summary, incidents = create_incident_filter(
            release_date_lower=self.date_lower.isoformat(),
            release_date_upper=self.date_upper.isoformat()
        ).fetch()

        self.assertEqual(len(incidents), 2)
        self.assertTrue(target1 in incidents)
        self.assertTrue(target2 in incidents)

    def test_should_filter_correctly_with_equal_dates(self):
        """should filter correctly if upper and lower dates are equal"""
        target = IncidentPageFactory(
            release_date=self.date_lower
        )

        # This incident should not be included in the filer, because it is before the lower date
        IncidentPageFactory(
            release_date=(self.date_lower - timedelta(days=1))
        )
        IncidentPageFactory(
            release_date=(self.date_lower + timedelta(days=1))
        )

        summary, incidents = create_incident_filter(
            release_date_lower=self.date_lower.isoformat(),
            release_date_upper=self.date_lower.isoformat()
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)
