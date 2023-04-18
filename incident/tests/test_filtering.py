from datetime import date, timedelta
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.http import QueryDict
from django.test import TestCase
from django.utils import timezone
from wagtail.models import Site
from wagtail.rich_text import RichText

from common.models import CategoryPage
from common.models.settings import IncidentFilterSettings, GeneralIncidentFilter
from common.tests.factories import CategoryPageFactory
from incident.models.choices import (
    ARREST_STATUS,
    DETENTION_STATUS,
    STATUS_OF_CHARGES,
    STATUS_OF_PRIOR_RESTRAINT,
    STATUS_OF_SEIZED_EQUIPMENT,
    SUBPOENA_STATUS,
)
from incident.tests.factories import (
    ChargeFactory,
    EquipmentSeizedFactory,
    EquipmentBrokenFactory,
    IncidentPageFactory,
    IncidentIndexPageFactory,
    IncidentUpdateFactory,
    InexactDateIncidentPageFactory,
    StateFactory,
    InstitutionFactory,
    JournalistFactory,
    TargetedJournalistFactory,
    LawEnforcementOrganizationFactory,
    NationalityFactory,
    IncidentChargeFactory,
    IncidentChargeWithUpdatesFactory,
)
from incident.utils.incident_filter import IncidentFilter, ManyRelationValue, SearchFilter


class TestFiltering(TestCase):
    """Incident filters"""
    @classmethod
    def setUpTestData(cls):
        cls.index = IncidentIndexPageFactory()

    def test_should_filter_by_search_text(self):
        """should filter by search text."""
        incident1 = IncidentPageFactory(
            body=[('rich_text', RichText('eggplant'))],
        )
        IncidentPageFactory(
            body=[('rich_text', RichText('science fiction'))],
        )

        incidents = IncidentFilter(dict(
            search='eggplant',
        )).get_queryset()

        self.assertEqual({incident1}, set(incidents))

    def test_should_filter_by_search_text_with_null_characters(self):
        """should filter by search text with null characters."""
        incident1 = IncidentPageFactory(
            body=[('rich_text', RichText('eggplant'))],
        )
        IncidentPageFactory(
            body=[('rich_text', RichText('science fiction'))],
        )

        incidents = IncidentFilter(
            QueryDict('search=eggplant%00')
        ).get_queryset()

        self.assertQuerysetEqual(incidents, [incident1])

    def test_sorting_by_invalid_value_adds_errors(self):
        incident_filter = IncidentFilter(
            QueryDict.fromkeys(['sort'], value='INVALID')
        )
        with self.assertRaises(ValidationError) as cm:
            incident_filter.clean(strict=True)
        self.assertEqual(
            [str(error) for error in cm.exception],
            ['Invalid sort option: "INVALID"']
        )

    def test_sorts_by_newest_incident_date(self):
        incident2 = IncidentPageFactory(date='2022-02-02')
        incident1 = IncidentPageFactory(date='2022-03-03')
        incident3 = IncidentPageFactory(date='2022-01-01')

        incidents = IncidentFilter(
            QueryDict.fromkeys(['sort'], value='NEWEST')
        ).get_queryset()

        self.assertEqual([incident1, incident2, incident3], list(incidents))

    def test_sorts_by_newest_incident_date_by_default(self):
        incident2 = IncidentPageFactory(date='2022-02-02')
        incident1 = IncidentPageFactory(date='2022-03-03')
        incident3 = IncidentPageFactory(date='2022-01-01')

        incidents = IncidentFilter(QueryDict()).get_queryset()

        self.assertEqual([incident1, incident2, incident3], list(incidents))

    def test_sorts_by_oldest_incident_date(self):
        incident3 = IncidentPageFactory(date='2022-03-03')
        incident1 = IncidentPageFactory(date='2022-01-01')
        incident2 = IncidentPageFactory(date='2022-02-02')

        incidents = IncidentFilter(
            QueryDict.fromkeys(['sort'], value='OLDEST')
        ).get_queryset()

        self.assertEqual([incident1, incident2, incident3], list(incidents))

    def test_sorts_by_recently_updated(self):
        incident4 = IncidentPageFactory(date='2022-04-04')  # has no update
        incident3 = IncidentPageFactory(date='2022-01-01')
        incident1 = IncidentPageFactory(date='2022-02-02')
        incident2 = IncidentPageFactory(date='2022-03-03')

        dt1 = timezone.now() - timedelta(days=1)
        dt2 = timezone.now() - timedelta(days=2)
        dt3 = timezone.now() - timedelta(days=3)

        IncidentUpdateFactory(page=incident1, date=dt1)
        IncidentUpdateFactory(page=incident2, date=dt2)
        IncidentUpdateFactory(page=incident3, date=dt3)

        incidents = IncidentFilter(
            QueryDict.fromkeys(['sort'], value='RECENTLY_UPDATED')
        ).get_queryset()

        self.assertEqual(
            [incident1, incident2, incident3, incident4],
            list(incidents),
        )

    def test_should_filter_by_nationality_title(self):
        category1 = CategoryPageFactory(
            incident_filters=['target_nationality'],
        )
        nat1 = NationalityFactory(title='A')
        nat2 = NationalityFactory(title='B')
        nat3 = NationalityFactory(title='C')

        incident1 = IncidentPageFactory(categories=[category1])
        incident1.target_nationality.add(nat1)
        incident1.save()
        incident2 = IncidentPageFactory(categories=[category1])
        incident2.target_nationality.add(nat2)
        incident2.save()
        incident3 = IncidentPageFactory(categories=[category1])
        incident3.target_nationality.add(nat3)
        incident3.save()
        incidents = IncidentFilter(
            {
                'target_nationality': nat3.title,
                'categories': str(category1.pk),
            }
        ).get_queryset()
        self.assertEqual(set(incidents), {incident3})

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

    def test_should_filter_by_all_categories_given_negative(self):
        """should combine multiple categories using AND logic."""
        category1 = CategoryPageFactory()
        category2 = CategoryPageFactory()
        category3 = CategoryPageFactory()

        IncidentPageFactory(categories=[category1, category3])
        IncidentPageFactory(categories=[category2])

        incidents = IncidentFilter(dict(
            categories=f'{category2.pk},{category3.pk}',
        )).get_queryset()
        self.assertQuerysetEqual([], incidents)

    def test_should_filter_by_all_categories_given_positive(self):
        """should combine multiple categories using AND logic."""
        category1 = CategoryPageFactory()
        category2 = CategoryPageFactory()
        category3 = CategoryPageFactory()

        incident1 = IncidentPageFactory(categories=[category1, category3])
        IncidentPageFactory(categories=[category2])
        IncidentPageFactory(categories=[category1])

        incidents = IncidentFilter(dict(
            categories=f'{category1.pk},{category3.pk}',
        )).get_queryset()
        self.assertQuerysetEqual(incidents, [incident1])

    def test_should_filter_by_category_name(self):
        category1 = CategoryPageFactory(title='Eukarya')
        category2 = CategoryPageFactory(title='Eubacteria')
        category3 = CategoryPageFactory(title='Archaea')
        IncidentPageFactory(categories=[category1, category3])
        IncidentPageFactory(categories=[category2])
        incident3 = IncidentPageFactory(categories=[category1, category2])
        incident4 = IncidentPageFactory(categories=[category1, category2])

        incidents = IncidentFilter(
            {'categories': f'{category1.title},{category2.title}'}
        ).get_queryset()
        self.assertQuerysetEqual(incidents, [incident3, incident4])

    def test_should_filter_by_char_field(self):
        """should filter via a field that is a char field"""
        city = 'albuquerque'
        uppercase_city = 'Albuquerque'
        target = IncidentPageFactory(
            city=city,
        )
        IncidentPageFactory(
            city='other'
        )
        incidents = IncidentFilter(dict(
            city=city
        )).get_queryset()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

        incidents = IncidentFilter(dict(
            city=uppercase_city
        )).get_queryset()
        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_circuit(self):
        # See incident/circuits.py
        GeneralIncidentFilter.objects.all().delete()
        CategoryPage.objects.all().delete()
        site = Site.objects.get(is_default_site=True)
        settings = IncidentFilterSettings.for_site(site)
        GeneralIncidentFilter.objects.create(
            incident_filter_settings=settings,
            incident_filter='circuits',
        )
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
        """Filter should filter charges regardless of status"""
        category = CategoryPageFactory(
            title='Arrest / Criminal Charge',
            incident_filters=['charges'],
        )
        charge = ChargeFactory()
        target1 = IncidentPageFactory(categories=[category])
        target2 = IncidentPageFactory(categories=[category])
        IncidentPageFactory(categories=[category])

        IncidentChargeFactory(
            incident_page=target1,
            charge=charge,
        )
        IncidentChargeFactory(
            incident_page=target2,
            charge=charge,
        )

        incidents = IncidentFilter(dict(
            categories=str(category.id),
            charges=str(charge.pk),
        )).get_queryset()
        self.assertQuerysetEqual(incidents, [target1, target2])

    def test_should_filter_charges_by_title_as_one_field(self):
        """Filter should filter charges by title as if current and dropped charges are a single field"""
        category = CategoryPageFactory(
            title='Arrest / Criminal Charge',
            incident_filters=['charges'],
        )
        charge = ChargeFactory()
        target1 = IncidentPageFactory(categories=[category])
        target2 = IncidentPageFactory(categories=[category])
        IncidentPageFactory(categories=[category])

        IncidentChargeFactory(
            incident_page=target1,
            charge=charge,
        )
        IncidentChargeFactory(
            incident_page=target2,
            charge=charge,
        )
        incidents = IncidentFilter(dict(
            categories=str(category.id),
            charges=charge.title,
        )).get_queryset()

        self.assertQuerysetEqual(incidents, [target1, target2])

    def test_should_filter_incidents_by_most_recent_status(self):
        category = CategoryPageFactory(
            title='Arrest / Criminal Charge',
            incident_filters=['status_of_charges'],
        )
        desired_status = 'PENDING_APPEAL'
        target1 = IncidentPageFactory(categories=[category])
        target2 = IncidentPageFactory(categories=[category])
        IncidentPageFactory(categories=[category])
        IncidentChargeWithUpdatesFactory(
            incident_page=target1,
            status='UNKNOWN',
            date='2022-01-01',
            update1__status='CHARGES_PENDING',
            update1__date='2022-01-02',
            update2__status='CONVICTED',
            update2__date='2022-01-03',
            update3__status=desired_status,
            update3__date='2022-01-04',
        )
        IncidentChargeWithUpdatesFactory(
            incident_page=target2,
            status='UNKNOWN',
            date='2022-01-01',
            update1__status='CHARGES_PENDING',
            update1__date='2022-01-02',
            update2__status=desired_status,
            update2__date='2022-01-03',
            update3__status='CHARGES_DROPPED',
            update3__date='2022-01-04',
        )
        incidents = IncidentFilter(dict(
            categories=str(category.id),
            status_of_charges=desired_status,
        )).get_queryset(strict=True)

        self.assertQuerysetEqual(incidents, [target1])

    def test_filters_by_charge_update_status_for_same_date_updates(self):
        """ChargeUpdates should have priority when filtering by status

        When a charge has an update applied on the same day, the
        filter should assume the "most recent" status is stored on the
        ChargeUpdate, not on the IncidentCharge itself.  Meaning if a
        an incident has status update happen on the same date as the
        charge was created, filtering by the "initial" status should
        not find the that incident.

        """
        category = CategoryPageFactory(
            title='Arrest / Criminal Charge',
            incident_filters=['status_of_charges'],
        )
        undesired_status = 'CHARGES_PENDING'
        desired_status = 'CHARGES_DROPPED'
        target1 = IncidentPageFactory(categories=[category])
        IncidentChargeWithUpdatesFactory(
            incident_page=target1,
            status=undesired_status,
            date='2022-01-01',
            update1__status=desired_status,
            update1__date='2022-01-01',
            update2=None,
            update3=None,
        )
        incidents = IncidentFilter(dict(
            categories=str(category.id),
            status_of_charges=undesired_status,
        )).get_queryset(strict=True)

        self.assertQuerysetEqual(incidents, [])

        incidents = IncidentFilter(dict(
            categories=str(category.id),
            status_of_charges=desired_status,
        )).get_queryset(strict=True)
        self.assertQuerysetEqual(incidents, [target1])


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


class TestAllFiltersAtOnce:
    """Base class for testing all filters at once."""

    filters_to_skip = {'index_entries', 'wagtail_admin_comments', 'subscribers'}

    @classmethod
    def setUpTestData(cls):
        cls.available_filters = IncidentFilter.get_available_filters()
        cls.category = CategoryPageFactory(
            incident_filters=cls.available_filters,
        )

    @property
    def category_id(self):
        """Should return the category ID value to be used by the test case.

        The category filter is a special filter because it is used to
        determine the validity of other filters in a set of filter
        data.  This test class relies on a systematic mapping of
        filters to values, but this can cause problems if the value of
        the category filter is not set to a specific ID value, which
        is not known before the tests are being run.  So this function
        exists to provide that value separately from the rest of the
        filters due to its importance.

        """
        raise NotImplementedError()

    def value_for_field(self, fltr):
        """Takes a Filter class and returns a value.

        Function must be implemented by individual test cases.  This
        is called on every filter to generate a filter value to be
        used as data by the IncidentFilter class.  It can a simple
        value, which will be applied to the filter data under a key
        with the same name as the filter, or return a dictionary,
        which will be merged into the overall filter data.  The latter
        is useful for filters that accept multiple values, such as
        upper/lower date filters.

        """
        raise NotImplementedError()

    def all_filters(self):
        """Generator that yields all filters for the purposes of this test.

        Includes all available filters, the search filter, and *not*
        the Category filter.  The latter of which is a special-case
        which must be handled seprately.

        """
        yield SearchFilter()
        for category_filter in self.category.incident_filters.all():
            fltr = self.available_filters[category_filter.incident_filter]
            if fltr.name in {'categories'} | self.filters_to_skip:
                # Always skip categories, it's handled in a special case.
                continue
            yield fltr

    def setUp(self):
        filter_data = {
            'categories': self.category_id,
        }
        for fltr in self.all_filters():
            value = self.value_for_field(fltr)
            if isinstance(value, dict):
                filter_data.update(value)
            else:
                filter_data[fltr.name] = value
        self.incident_filter = IncidentFilter(filter_data)

    def test_queryset_is_obtainable(self):
        # This test passes if the following functions complete with no
        # errors, and the cleaned filters match our expectations.
        self.incident_filter.clean(strict=True)
        self.incident_filter.get_queryset()
        self.incident_filter.get_summary()

        self.assertEqual(
            set(self.incident_filter.cleaned_data),
            {
                filter_name
                for filter_name in IncidentFilter.get_available_filters()
                if filter_name not in self.filters_to_skip
            } | {
                'date',
                'detention_date',
                'release_date',
                'search',
                'categories',
            }
        )


class TestAllFiltersCombinedWithSearch(TestAllFiltersAtOnce, TestCase):
    @property
    def category_id(self):
        return str(self.category.pk)

    def value_for_field(self, fltr):
        field = fltr.serialize()
        name = fltr.name
        t = field['type']
        if t == 'text':
            return 'value'
        elif t == 'pk' or t == 'autocomplete':
            return '1'
        elif t == 'choice' or t == 'radio':
            filter_ = self.available_filters[field['name']]
            return list(filter_.get_choices())[0]
        elif t == 'bool':
            return 'True'
        elif t == 'int':
            return '1'
        elif t == 'date':
            return {
                f'{name}_lower': '2011-01-01',
                f'{name}_upper': '2012-01-01',
            }
        else:
            raise ValueError(f'Could not determine value for field of type {t!r}')


class TestAllFiltersForNullCharacterSafety(TestAllFiltersAtOnce, TestCase):
    @property
    def category_id(self):
        return str(self.category.pk) + '\x00'

    # get a valid value for a given field
    def value_for_field(self, fltr):
        field = fltr.serialize()
        name = fltr.name
        t = field['type']
        if t == 'text':
            return 'value\x00'
        elif t == 'pk' or t == 'autocomplete':
            return '1\x00'
        elif t == 'choice' or t == 'radio':
            filter_ = self.available_filters[field['name']]
            choice = list(filter_.get_choices())[0]
            return f'{choice}\x00'
        elif t == 'bool':
            return 'True\x00'
        elif t == 'int':
            return '1\x00'
        elif t == 'date':
            return {
                f'{name}_lower': '2011\x00-01-01',
                f'{name}_upper': '2012\x00-01-01',
            }
        else:
            raise ValueError(f'Could not determine value for field of type {t!r}')


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
            'categories': ManyRelationValue(pks=[self.category.id]),
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
            city='other',
            categories=[self.category],
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            status_of_seized_equipment="hello",
        ))

        incidents = incident_filter.get_queryset()
        self.assertEqual(incidents.count(), 3)
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id]),
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
            'categories': ManyRelationValue(pks=[self.category.id]),
            'status_of_seized_equipment': [self.custody, self.returned_full],
        })


class MultiChoiceFilterTest(TestCase):
    def setUp(self):
        self.pending = 'PENDING'
        self.dropped = 'DROPPED'
        self.quashed = 'QUASHED'
        self.category = CategoryPageFactory(
            title='Subpoena / Legal Order',
            incident_filters=['subpoena_statuses'],
        )

    def test_should_filter_by_choice_field(self):
        """should filter via a field that is a choice field"""

        target = IncidentPageFactory(
            subpoena_statuses=[self.pending],
            categories=[self.category],
        )
        IncidentPageFactory(
            subpoena_statuses=[self.dropped],
            categories=[self.category],
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            subpoena_statuses=self.pending,
        ))

        incidents = incident_filter.get_queryset()
        self.assertEqual(incidents.count(), 1)
        self.assertIn(target, incidents)
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id]),
            'subpoena_statuses': [self.pending],
        })

    def test_filter_should_return_all_if_choice_field_invalid(self):
        """should not filter if choice is invalid"""

        IncidentPageFactory(
            subpoena_statuses=[self.pending],
            categories=[self.category],
        )
        IncidentPageFactory(
            subpoena_statuses=[self.dropped],
            categories=[self.category],
        )
        IncidentPageFactory(
            city='other',
            categories=[self.category],
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            subpoena_statuses="hello",
        ))

        incidents = incident_filter.get_queryset()
        self.assertEqual(incidents.count(), 3)
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id]),
        })

    def test_filter_should_handle_field_with_multiple_values(self):
        """should handle multiple choices"""
        target = IncidentPageFactory(
            subpoena_statuses=[self.pending, self.dropped],
            categories=[self.category],
        )
        IncidentPageFactory(
            subpoena_statuses=[self.dropped],
            categories=[self.category],
        )
        IncidentPageFactory(
            subpoena_statuses=[self.pending],
            categories=[self.category],
        )

        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            subpoena_statuses=self.pending,
        ))

        incidents = incident_filter.get_queryset()
        self.assertEqual(incidents.count(), 2)
        self.assertIn(target, incidents)
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id]),
            'subpoena_statuses': [self.pending],
        })

    def test_filter_should_handle_multiple_choices(self):
        """should handle multiple choices"""
        target1 = IncidentPageFactory(
            subpoena_statuses=[self.pending],
            categories=[self.category],
        )
        target2 = IncidentPageFactory(
            subpoena_statuses=[self.dropped],
            categories=[self.category],
        )
        target3 = IncidentPageFactory(
            subpoena_statuses=[self.pending, self.dropped],
            categories=[self.category],
        )
        IncidentPageFactory(
            subpoena_statuses=[self.quashed],
            categories=[self.category],
        )

        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            subpoena_statuses='{0},{1}'.format(self.pending, self.dropped),
        ))

        incidents = incident_filter.get_queryset()
        self.assertEqual(incidents.count(), 3)
        self.assertIn(target1, incidents)
        self.assertIn(target2, incidents)
        self.assertIn(target3, incidents)
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id]),
            'subpoena_statuses': [self.pending, self.dropped],
        })


class GetSummaryTest(TestCase):
    def setUp(self):
        self.custody = 'CUSTODY'
        self.returned_full = 'RETURNED_FULL'
        self.category = CategoryPageFactory(
            title='Equipment Search or Seizure',
            incident_filters=['status_of_seized_equipment'],
        )

    def test_summary__january(self):
        "Summary should correctly count incidents in January"

        # Two incidents in January 2018, two not
        IncidentPageFactory(date=date(2018, 1, 15), journalist_targets=1, institution_targets=1, journalist_targets__institution=None)
        IncidentPageFactory(date=date(2018, 1, 16), journalist_targets=1, institution_targets=1, journalist_targets__institution=None)
        IncidentPageFactory(date=date(2017, 1, 15), journalist_targets=1, institution_targets=1, journalist_targets__institution=None)
        IncidentPageFactory(date=date(2018, 2, 15), journalist_targets=1, institution_targets=1, journalist_targets__institution=None)

        with patch('incident.utils.incident_filter.date') as date_:
            date_.today = lambda: date(2018, 1, 20)
            summary = IncidentFilter({}).get_summary()

        self.assertCountEqual(summary, (
            ('Total Results', 4),
            ('Journalists affected', 4),
            ('Institutions affected', 4),
            ('Results in 2018', 3),
            ('Results in January', 2)
        ))

    def test_summary__december(self):
        "Summary should correctly count incidents in December"

        # Two incidents in December 2018, two not
        IncidentPageFactory(date=date(2018, 12, 15), journalist_targets=2, journalist_targets__institution=None)
        IncidentPageFactory(date=date(2018, 12, 16), journalist_targets=2, journalist_targets__institution=None)
        IncidentPageFactory(date=date(2019, 1, 1), journalist_targets=2, journalist_targets__institution=None)
        IncidentPageFactory(date=date(2018, 2, 15), journalist_targets=2, journalist_targets__institution=None)

        with patch('incident.utils.incident_filter.date') as date_:
            date_.today = lambda: date(2018, 12, 20)
            summary = IncidentFilter({}).get_summary()

        self.assertCountEqual(summary, (
            ('Total Results', 4),
            ('Journalists affected', 8),
            ('Institutions affected', 8),
            ('Results in 2018', 3),
            ('Results in December', 2)
        ))

    def test_single_category_excludes_category_count(self):
        IncidentPageFactory(
            status_of_seized_equipment=self.custody,
            categories=[self.category],
            date=timezone.now().date(),
            journalist_targets=0,
            institution_targets=0,
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.returned_full,
            categories=[self.category],
            date=timezone.now().date(),
            journalist_targets=0,
            institution_targets=0,
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            status_of_seized_equipment=self.custody,
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 1),
            ('Journalists affected', 0),
            ('Institutions affected', 0),
            ('Results in {}'.format(timezone.now().year), 1),
            ('Results in {0:%B}'.format(timezone.now().date()), 1),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id]),
            'status_of_seized_equipment': [self.custody],
        })

    def test_category_incident_count_filtered(self):
        category2 = CategoryPageFactory(
            title='Other category',
        )
        IncidentPageFactory(
            lawsuit_name='Lawsuit One',
            categories=[self.category, category2],
            date=timezone.now().date(),
        )
        IncidentPageFactory(
            lawsuit_name='Lawsuit Two',
            categories=[self.category, category2],
            date=timezone.now().date(),
        )
        IncidentPageFactory(
            lawsuit_name='Lawsuit One',
            categories=[category2, self.category],
            date=timezone.now().date(),
        )
        incident_filter = IncidentFilter(dict(
            categories='{},{}'.format(self.category.id, category2.id),
            lawsuit_name='Lawsuit One',
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 2),
            ('Journalists affected', 0),
            ('Institutions affected', 4),
            ('Results in {}'.format(timezone.now().year), 2),
            ('Results in {0:%B}'.format(timezone.now().date()), 2),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id, category2.id]),
            'lawsuit_name': 'Lawsuit One',
        })

    def test_category_incident_count_filtered_by_title(self):
        category2 = CategoryPageFactory(
            title='Other category',
        )
        IncidentPageFactory(
            lawsuit_name='Lawsuit One',
            categories=[self.category, category2],
            date=timezone.now().date(),
        )
        IncidentPageFactory(
            lawsuit_name='Lawsuit Two',
            categories=[self.category, category2],
            date=timezone.now().date(),
        )
        IncidentPageFactory(
            lawsuit_name='Lawsuit One',
            categories=[category2, self.category],
            date=timezone.now().date(),
        )
        incident_filter = IncidentFilter(dict(
            categories='{},{}'.format(self.category.pk, category2.title),
            lawsuit_name='Lawsuit One',
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 2),
            ('Journalists affected', 0),
            ('Institutions affected', 4),
            ('Results in {}'.format(timezone.now().year), 2),
            ('Results in {0:%B}'.format(timezone.now().date()), 2),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(
                pks=[self.category.pk],
                strings=[category2.title]),
            'lawsuit_name': 'Lawsuit One',
        })

    def test_target_count__filtered(self):
        # Matched incident page
        IncidentPageFactory(
            status_of_seized_equipment=self.custody,
            categories=[self.category],
            date=timezone.now().date(),
            journalist_targets=3,
            institution_targets=3,
            journalist_targets__institution=None,
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.returned_full,
            categories=[self.category],
            date=timezone.now().date(),
            journalist_targets=5,
            institution_targets=5,
            journalist_targets__institution=None,
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
            status_of_seized_equipment=self.custody,
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 1),
            ('Journalists affected', 3),
            ('Institutions affected', 3),
            ('Results in {}'.format(timezone.now().year), 1),
            ('Results in {0:%B}'.format(timezone.now().date()), 1),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id]),
            'status_of_seized_equipment': [self.custody],
        })

    def test_target_journalist_count__combined(self):
        IncidentPageFactory(
            categories=[self.category],
            date=timezone.now().date(),
            journalist_targets=3,
            institution_targets=0,
            journalist_targets__institution=None,
        )
        IncidentPageFactory(
            categories=[self.category],
            date=timezone.now().date(),
            journalist_targets=5,
            institution_targets=0,
            journalist_targets__institution=None,
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 2),
            ('Journalists affected', 8),
            ('Institutions affected', 0),
            ('Results in {}'.format(timezone.now().year), 2),
            ('Results in {0:%B}'.format(timezone.now().date()), 2),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id]),
        })

    def test_journalist_count__deduped(self):
        journalist1 = JournalistFactory()
        journalist2 = JournalistFactory()
        incident1 = IncidentPageFactory(
            categories=[self.category],
            date=timezone.now().date(),
            institution_targets=0,
        )
        TargetedJournalistFactory(incident=incident1, journalist=journalist1, institution=None)
        TargetedJournalistFactory(incident=incident1, journalist=journalist2, institution=None)

        incident2 = IncidentPageFactory(
            categories=[self.category],
            date=timezone.now().date(),
            institution_targets=0,
        )
        TargetedJournalistFactory(incident=incident2, journalist=journalist1, institution=None)

        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 2),
            ('Journalists affected', 2),
            ('Institutions affected', 0),
            ('Results in {}'.format(timezone.now().year), 2),
            ('Results in {0:%B}'.format(timezone.now().date()), 2),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id]),
        })

    def test_institution_count__deduped(self):
        inst1 = InstitutionFactory()
        inst2 = InstitutionFactory()
        incident1 = IncidentPageFactory(
            categories=[self.category],
            date=timezone.now().date(),
            institution_targets=0,
        )
        incident1.targeted_institutions.set([inst1, inst2])
        incident1.save()

        incident2 = IncidentPageFactory(
            categories=[self.category],
            date=timezone.now().date(),
            institution_targets=0,
        )
        incident2.targeted_institutions.set([inst1])
        incident2.save()

        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
        ))

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 2),
            ('Journalists affected', 0),
            ('Institutions affected', 2),
            ('Results in {}'.format(timezone.now().year), 2),
            ('Results in {0:%B}'.format(timezone.now().date()), 2),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id]),
        })

    def test_institution_count__via_journalists(self):
        InstitutionFactory()

        TargetedJournalistFactory(
            incident__institution_targets=0,
            incident__categories=[self.category],
            incident__title='Test Incident',
        )
        incident_filter = IncidentFilter(dict(
            categories=str(self.category.id),
        ))
        summary = incident_filter.get_summary()
        institutions_affected = dict(summary)['Institutions affected']
        self.assertEqual(institutions_affected, 1)

    def test_search__no_categories(self):
        # Matched incident page
        IncidentPageFactory(
            title='asdf',
            date=timezone.now().date(),
            journalist_targets=3,
            journalist_targets__institution=None,
        )
        IncidentPageFactory(
            title='zxcv',
            date=timezone.now().date(),
            journalist_targets=5,
            journalist_targets__institution=None,
        )
        incident_filter = IncidentFilter({
            'search': 'asdf',
        })

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 1),
            ('Journalists affected', 3),
            ('Institutions affected', 2),
            ('Results in {}'.format(timezone.now().year), 1),
            ('Results in {0:%B}'.format(timezone.now().date()), 1),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'search': 'asdf',
        })

    def test_search__filters_categories(self):
        category2 = CategoryPageFactory(
            title='Other category',
        )
        # Matched incident page
        IncidentPageFactory(
            title='asdf 1',
            categories=[self.category, category2],
            date=timezone.now().date(),
            journalist_targets=3,
            journalist_targets__institution=None,
        )
        IncidentPageFactory(
            title='zxcv',
            categories=[self.category, category2],
            date=timezone.now().date(),
            journalist_targets=5,
            journalist_targets__institution=None,
        )
        IncidentPageFactory(
            title='asdf 2',
            categories=[category2, self.category],
            date=timezone.now().date(),
            journalist_targets=7,
            journalist_targets__institution=None,
        )
        incident_filter = IncidentFilter({
            'categories': '{},{}'.format(self.category.id, category2.id),
            'search': 'asdf',
        })

        summary = incident_filter.get_summary()
        self.assertEqual(summary, (
            ('Total Results', 2),
            ('Journalists affected', 10),
            ('Institutions affected', 4),
            ('Results in {}'.format(timezone.now().year), 2),
            ('Results in {0:%B}'.format(timezone.now().date()), 2),
        ))
        self.assertEqual(incident_filter.cleaned_data, {
            'categories': ManyRelationValue(pks=[self.category.id, category2.id]),
            'search': 'asdf',
        })


class FilterChoicesTest(TestCase):
    def test_filter_choices_alphabetical(self):
        """
        To ensure that choices are ordered deterministically they should be
        sorted alphabetically
        """
        choices_iterator = IncidentFilter.get_filter_choices()
        choices = [x for x in choices_iterator]
        self.assertSequenceEqual(
            choices,
            sorted(choices, key=lambda t: t[1])
        )


class PendingFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        CategoryPage.objects.all().delete()
        site = Site.objects.get(is_default_site=True)
        settings = IncidentFilterSettings.for_site(site)
        GeneralIncidentFilter.objects.create(
            incident_filter='pending_cases',
            incident_filter_settings=settings,
        )

        cls.all_incidents = {
            # Incident not associated with any pending statuses.
            IncidentPageFactory(),
        }

        for value, _ in ARREST_STATUS:
            cls.all_incidents.add(IncidentPageFactory(arrest_status=value))
        for value, _ in STATUS_OF_CHARGES:
            cls.all_incidents.add(IncidentPageFactory(status_of_charges=value))
        for value, _ in STATUS_OF_SEIZED_EQUIPMENT:
            cls.all_incidents.add(IncidentPageFactory(status_of_seized_equipment=value))
        for value, _ in SUBPOENA_STATUS:
            cls.all_incidents.add(IncidentPageFactory(subpoena_statuses=[value]))
        for value, _ in DETENTION_STATUS:
            cls.all_incidents.add(IncidentPageFactory(detention_status=value))
        for value, _ in STATUS_OF_PRIOR_RESTRAINT:
            cls.all_incidents.add(IncidentPageFactory(status_of_prior_restraint=value))

    def test_filter__true(self):
        """
        If the pending cases filter is on, only incidents with "pending"
        values should be included. The rest should be excluded.
        """
        incidents = IncidentFilter({
            'pending_cases': 'True',
        }).get_queryset()

        values = []
        fields = [
            'arrest_status',
            'status_of_charges',
            'status_of_seized_equipment',
            'subpoena_statuses',
            'detention_status',
            'status_of_prior_restraint',
        ]

        for incident in incidents:
            for field in fields:
                value = getattr(incident, field)
                if value:
                    values.append((field, value))
                    break

        self.assertCountEqual(values, [
            ('arrest_status', 'DETAINED_CUSTODY'),
            ('arrest_status', 'ARRESTED_CUSTODY'),
            ('status_of_charges', 'CHARGES_PENDING'),
            ('status_of_charges', 'PENDING_APPEAL'),
            ('status_of_seized_equipment', 'CUSTODY'),
            ('status_of_seized_equipment', 'RETURNED_PART'),
            ('subpoena_statuses', ['PENDING']),
            ('detention_status', 'IN_JAIL'),
            ('status_of_prior_restraint', 'PENDING'),
        ])

    def test_filter__false(self):
        """
        If the pending cases filter is off, it should have no effect.
        """
        incidents = IncidentFilter({
            'pending_cases': 'False',
        }).get_queryset()

        self.assertCountEqual(incidents, self.all_incidents)

    def test_filter__invalid(self):
        """
        If the pending cases filter is invalid, it should have no effect.
        """
        incidents = IncidentFilter({
            'pending_cases': 'Hello',
        }).get_queryset()

        self.assertCountEqual(incidents, self.all_incidents)

    def test_filter__none(self):
        """
        If the pending cases filter is not supplied, it should have no effect.
        """
        incidents = IncidentFilter({}).get_queryset()

        self.assertCountEqual(incidents, self.all_incidents)


class StateFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        site = Site.objects.get(is_default_site=True)
        settings = IncidentFilterSettings.for_site(site)
        GeneralIncidentFilter.objects.create(
            incident_filter='state',
            incident_filter_settings=settings,
        )
        cls.new_mexico = StateFactory(name='New Mexico', abbreviation='NM')
        cls.alaska = StateFactory(name='Alaska', abbreviation='AK')

    def test_uses_noninteger_parameters_to_query_abbreviation(self):
        IncidentPageFactory(state=self.new_mexico)
        incident2 = IncidentPageFactory(state=self.alaska)

        incident_filter = IncidentFilter({
            'state': 'AK',
        })

        incident_filter.clean()
        incidents = incident_filter.get_queryset()

        self.assertEqual(set(incidents), {incident2})

    def test_uses_noninteger_parameters_to_query_name(self):
        incident1 = IncidentPageFactory(state=self.new_mexico)
        IncidentPageFactory(state=self.alaska)

        incident_filter = IncidentFilter({
            'state': 'New Mexico',
        })

        incident_filter.clean()
        incidents = incident_filter.get_queryset()

        self.assertEqual(set(incidents), {incident1})

    def test_filters_foreign_key_relationships_by_id(self):
        incident1 = IncidentPageFactory(state=self.new_mexico)
        IncidentPageFactory(state=self.alaska)

        incident_filter = IncidentFilter({'state': str(self.new_mexico.pk)})
        incident_filter.clean()
        incidents = incident_filter.get_queryset()

        self.assertEqual(set(incidents), {incident1})


class EquipmentFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        site = Site.objects.get(is_default_site=True)
        settings = IncidentFilterSettings.for_site(site)
        for name in ('equipment_seized', 'equipment_broken'):
            GeneralIncidentFilter.objects.create(
                incident_filter=name,
                incident_filter_settings=settings,
            )

    def test_seized_equipment_uses_noninteger_parameters_to_query_name(self):
        incident1 = IncidentPageFactory()
        incident2 = IncidentPageFactory()
        seized1 = EquipmentSeizedFactory(incident=incident1)
        EquipmentSeizedFactory(incident=incident2)

        incident_filter = IncidentFilter({
            'equipment_seized': seized1.equipment.name,
        })

        incident_filter.clean()
        incidents = incident_filter.get_queryset()

        self.assertEqual(set(incidents), {incident1})

    def test_broken_equipment_uses_noninteger_parameters_to_query_name(self):
        incident1 = IncidentPageFactory()
        incident2 = IncidentPageFactory()
        broken1 = EquipmentBrokenFactory(incident=incident1)
        EquipmentBrokenFactory(incident=incident2)

        incident_filter = IncidentFilter({
            'equipment_broken': broken1.equipment.name,
        })

        incident_filter.clean()
        incidents = incident_filter.get_queryset()

        self.assertEqual(set(incidents), {incident1})


class RelationFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        site = Site.objects.get(is_default_site=True)
        settings = IncidentFilterSettings.for_site(site)
        GeneralIncidentFilter.objects.create(
            incident_filter='arresting_authority',
            incident_filter_settings=settings,
        )
        cls.leo1 = LawEnforcementOrganizationFactory(title='Org 1')
        cls.leo2 = LawEnforcementOrganizationFactory(title='Org 2')

    def test_uses_noninteger_parameters_to_query_title(self):
        IncidentPageFactory(arresting_authority=self.leo1)
        incident2 = IncidentPageFactory(arresting_authority=self.leo2)

        incident_filter = IncidentFilter({
            'arresting_authority': self.leo2.title,
        })

        incident_filter.clean()
        incidents = incident_filter.get_queryset()

        self.assertEqual(set(incidents), {incident2})

    def test_filters_foreign_key_relationships_by_id(self):
        incident1 = IncidentPageFactory(arresting_authority=self.leo1)
        IncidentPageFactory(arresting_authority=self.leo2)

        incident_filter = IncidentFilter({'arresting_authority': str(self.leo1.pk)})
        incident_filter.clean()
        incidents = incident_filter.get_queryset()

        self.assertEqual(set(incidents), {incident1})


class RelationThroughTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        CategoryPage.objects.all().delete()
        site = Site.objects.get(is_default_site=True)
        settings = IncidentFilterSettings.for_site(site)
        GeneralIncidentFilter.objects.create(
            incident_filter='targeted_journalists',
            incident_filter_settings=settings,
        )

        cls.tj1 = TargetedJournalistFactory()
        cls.tj2 = TargetedJournalistFactory()
        cls.tj3 = TargetedJournalistFactory()
        cls.multi_journalist_incident = IncidentPageFactory(title='Multi')
        cls.tj4 = TargetedJournalistFactory(
            journalist=cls.tj1.journalist,
            incident=cls.multi_journalist_incident,
        )
        cls.tj5 = TargetedJournalistFactory(
            journalist=cls.tj3.journalist,
            incident=cls.multi_journalist_incident,
        )

    def test_filter_should_filter_by_single_journalist(self):
        incidents = IncidentFilter({
            'targeted_journalists': self.tj1.journalist.pk,
        }).get_queryset()

        self.assertQuerysetEqual(
            incidents,
            [self.tj1.incident, self.multi_journalist_incident],
        )

    def test_filter_should_filter_by_single_journalist_by_title(self):
        incidents = IncidentFilter({
            'targeted_journalists': self.tj1.journalist.title,
        }).get_queryset()

        self.assertQuerysetEqual(
            incidents,
            [self.tj1.incident, self.multi_journalist_incident],
        )

    def test_filter_should_filter_by_multiple_journalists(self):
        incidents = IncidentFilter({
            'targeted_journalists': '{},{}'.format(self.tj1.journalist.pk, self.tj3.journalist.pk),
        }).get_queryset()

        self.assertQuerysetEqual(incidents, [self.multi_journalist_incident])


class RecentlyUpdatedFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        site = Site.objects.get(is_default_site=True)
        settings = IncidentFilterSettings.for_site(site)
        GeneralIncidentFilter.objects.create(
            incident_filter='recently_updated',
            incident_filter_settings=settings,
        )

    def test_ignores_noninteger_parameters(self):
        incident_old = IncidentPageFactory(
            first_published_at=timezone.now() - timedelta(days=90),
        )
        incident_filter = IncidentFilter(
            {'recently_updated': 'xyz'}
        )

        incident_filter.clean()
        incidents = incident_filter.get_queryset()
        self.assertEqual(set(incidents), {incident_old})

    def test_filters_incidents_with_recent_updates(self):
        IncidentPageFactory(
            first_published_at=timezone.now() - timedelta(days=90),
        )

        incident_with_new_update = IncidentPageFactory(
            first_published_at=timezone.now() - timedelta(days=90),
        )
        IncidentUpdateFactory(
            page=incident_with_new_update,
            date=timezone.now() - timedelta(days=3),
        )

        incident_filter = IncidentFilter(QueryDict('recently_updated=10'))

        incident_filter.clean()
        incidents = incident_filter.get_queryset()
        self.assertEqual(set(incidents), {incident_with_new_update})

    def test_filters_recently_updated_excludes_nonupdated_incidents(self):
        IncidentPageFactory(
            first_published_at=timezone.now() - timedelta(days=90),
        )

        IncidentPageFactory(
            first_published_at=timezone.now() - timedelta(days=3),
        )

        incident_filter = IncidentFilter(QueryDict('recently_updated=10'))

        incident_filter.clean()
        incidents = incident_filter.get_queryset()
        self.assertEqual(set(incidents), set())

    def test_filters_recently_published_or_updated_incidents(self):
        """The recently_updated filter only includes incidents that have
        associated updates, no matter how recently they were
        published.

        """
        IncidentPageFactory(
            first_published_at=timezone.now() - timedelta(days=90),
        )
        incident_with_old_update = IncidentPageFactory(
            first_published_at=timezone.now() - timedelta(days=90),
        )
        IncidentUpdateFactory(
            page=incident_with_old_update,
            date=timezone.now() - timedelta(days=60),
        )

        incident_with_new_update = IncidentPageFactory(
            first_published_at=timezone.now() - timedelta(days=90),
        )
        IncidentUpdateFactory(
            page=incident_with_new_update,
            date=timezone.now() - timedelta(days=60),
        )
        IncidentUpdateFactory(
            page=incident_with_new_update,
            date=timezone.now() - timedelta(days=12),
        )

        IncidentPageFactory(
            first_published_at=timezone.now() - timedelta(days=3),
        )

        incident_filter = IncidentFilter(QueryDict('recently_updated=15'))

        incident_filter.clean()
        incidents = incident_filter.get_queryset()
        self.assertEqual(set(incidents), {incident_with_new_update})


class TargetedInstitutionsFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        GeneralIncidentFilter.objects.all().delete()
        site = Site.objects.get(is_default_site=True)
        settings = IncidentFilterSettings.for_site(site)
        GeneralIncidentFilter.objects.create(
            incident_filter='targeted_institutions',
            incident_filter_settings=settings,
        )

    def test_targeted_institution_filtering(self):
        inst1 = InstitutionFactory()
        inst2 = InstitutionFactory()
        IncidentPageFactory(
            institution_targets=0,
            title='Incident with no institutions targeted',
        )
        with_institution1_target = IncidentPageFactory(
            institution_targets=0,
            title='Incident with institution 1 directly targeted',
        )
        with_institution1_target.targeted_institutions.set([inst1])
        with_institution1_target.save()
        with_institution2_target = IncidentPageFactory(
            institution_targets=0,
            title='Incident with institution 2 directly targeted',
        )
        with_institution2_target.targeted_institutions.set([inst2])
        with_institution2_target.save()

        incident_filter = IncidentFilter({'targeted_institutions': inst1.pk})
        incident_filter.clean()

        incidents = incident_filter.get_queryset()
        self.assertQuerysetEqual(incidents, [with_institution1_target])

    def test_targeted_institution_filtering_by_title(self):
        inst1 = InstitutionFactory()
        inst2 = InstitutionFactory()
        IncidentPageFactory(
            institution_targets=0,
            title='Incident with no institutions targeted',
        )
        with_institution1_target = IncidentPageFactory(
            institution_targets=0,
            title='Incident with institution 1 directly targeted',
        )
        with_institution1_target.targeted_institutions.set([inst1])
        with_institution1_target.save()
        with_institution2_target = IncidentPageFactory(
            institution_targets=0,
            title='Incident with institution 2 directly targeted',
        )
        with_institution2_target.targeted_institutions.set([inst2])
        with_institution2_target.save()

        incident_filter = IncidentFilter(
            {'targeted_institutions': inst1.title},
        )
        incident_filter.clean()

        incidents = incident_filter.get_queryset()
        self.assertEqual(set(incidents), {with_institution1_target})

    def test_targeted_institution_multifiltering(self):
        inst1 = InstitutionFactory(title='Institution 1')
        inst2 = InstitutionFactory(title='Institution 2')
        IncidentPageFactory(
            institution_targets=0,
            title='Incident with no institutions targeted',
        )
        with_institution1_target = IncidentPageFactory(
            institution_targets=0,
            title='Incident with institution 1 directly targeted',
        )
        with_institution1_target.targeted_institutions.set([inst1])
        with_institution1_target.save()
        with_institution2_target = IncidentPageFactory(
            institution_targets=0,
            title='Incident with institution 2 directly targeted',
        )
        with_institution2_target.targeted_institutions.set([inst2])
        with_institution2_target.save()

        with_all_target = IncidentPageFactory(
            institution_targets=0,
            title='Incident with institutions 1 and 2 directly targeted',
        )
        with_all_target.targeted_institutions.add(inst1)
        with_all_target.targeted_institutions.add(inst2)
        with_all_target.save()

        incident_filter = IncidentFilter(
            # {'targeted_institutions': f'{inst1.pk},{inst2.title}'},
            {'targeted_institutions': f'{inst1.pk},{inst2.title}'},
        )
        incident_filter.clean()

        self.assertQuerysetEqual(
            incident_filter.get_queryset(),
            [with_all_target],
        )

        incident_filter = IncidentFilter(
            {'targeted_institutions': f'{inst1.title},{inst2.pk}'},
        )
        incident_filter.clean()
        self.assertQuerysetEqual(
            incident_filter.get_queryset(),
            [with_all_target],
            ordered=False,
        )

    def test_targeted_institution_filtering_via_targeted_journalists(self):
        tj1 = TargetedJournalistFactory(incident__title='Incident with Institution 1 targeted via journalist')
        TargetedJournalistFactory(incident__title='Incident with Institution 2 targeted via journalist')

        with_institution1_target = IncidentPageFactory(
            institution_targets=0,
            title='Incident with Institution 1 directly targeted',
        )
        with_institution1_target.targeted_institutions.set([tj1.institution])
        with_institution1_target.save()

        incident_filter = IncidentFilter({'targeted_institutions': tj1.institution.pk})
        incident_filter.clean()

        incidents = incident_filter.get_queryset()
        self.assertEqual(set(incidents), {tj1.incident, with_institution1_target})
