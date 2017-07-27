from itertools import chain
from datetime import date, timedelta

from django.test import TestCase
from wagtail.wagtailcore.rich_text import RichText

from incident.tests.factories import (
    IncidentPageFactory,
    IncidentIndexPageFactory,
    IncidentCategorizationFactory,
    InexactDateIncidentPageFactory,
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


def create_incident_filter(**kwargs):
    return IncidentFilter(
        search_text=kwargs.get('search_text', None),
        lower_date=kwargs.get('lower_date', None),
        upper_date=kwargs.get('upper_date', None),
        categories=kwargs.get('categories', None),
        targets=kwargs.get('targets', None),
        affiliation=kwargs.get('affiliation', None),
        state=kwargs.get('state', None),
        tags=kwargs.get('tags', None),
        city=kwargs.get('city', None),

        # Arrest/Detention
        arrest_status=kwargs.get('arrest_status', None),
        status_of_charges=kwargs.get('status_of_charges', None),
        current_charges=kwargs.get('current_charges', None),
        dropped_charges=kwargs.get('dropped_charges', None),
        detention_date_lower=kwargs.get('detention_date_lower', None),
        detention_date_upper=kwargs.get('detention_date_upper', None),
        release_date_lower=kwargs.get('release_date_lower', None),
        release_date_upper=kwargs.get('release_date_upper', None),
        unnecessary_use_of_force=kwargs.get('unnecessary_use_of_force', None),

        # LAWSUIT
        lawsuit_name=kwargs.get('lawsuit_name', None),
        venue=kwargs.get('venue', None),

        # EQUIPMENT
        equipment_seized=kwargs.get('equipment_seized', None),
        equipment_broken=kwargs.get('equipment_broken', None),
        status_of_seized_equipment=kwargs.get('status_of_seized_equipment', None),
        is_search_warrant_obtained=kwargs.get('is_search_warrant_obtained', None),
        actor=kwargs.get('actor', None),

        # BORDER STOP
        border_point=kwargs.get('border_point', None),
        stopped_at_border=kwargs.get('stopped_at_border', None),
        target_us_citizenship_status=kwargs.get('target_us_citizenship_status', None),
        denial_of_entry=kwargs.get('denial_of_entry', None),
        stopped_previously=kwargs.get('stopped_previously', None),
        target_nationality=kwargs.get('target_nationality', None),
        did_authorities_ask_for_device_access=kwargs.get('did_authorities_ask_for_device_access', None),
        did_authorities_ask_for_social_media_user=kwargs.get('did_authorities_ask_for_social_media_user', None),
        did_authorities_ask_for_social_media_pass=kwargs.get('did_authorities_ask_for_social_media_pass', None),
        did_authorities_ask_about_work=kwargs.get('did_authorities_ask_about_work', None),
        were_devices_searched_or_seized=kwargs.get('were_devices_searched_or_seized', None),

        # PHYSICAL ASSAULT
        assailant=kwargs.get('assailant', None),
        was_journalist_targeted=kwargs.get('was_journalist_targeted', None),

        # LEAK PROSECUTION
        charged_under_espionage_act=kwargs.get('charged_under_espionage_act', None),

        # SUBPOENA
        subpoena_type=kwargs.get('subpoena_type', None),
        subpoena_status=kwargs.get('subpoena_status', None),
        held_in_contempt=kwargs.get('held_in_contempt', None),
        detention_status=kwargs.get('detention_status', None),

        # LEGAL ORDER
        third_party_in_possession_of_communications=kwargs.get('third_party_in_possession_of_communications', None),
        third_party_business=kwargs.get('third_party_business', None),
        legal_order_type=kwargs.get('legal_order_type', None),

        # PRIOR RESTRAINT
        status_of_prior_restraint=kwargs.get('status_of_prior_restraint', None),
        # DENIAL OF ACCESS
        politicians_or_public_figures_involved=kwargs.get('politicians_or_public_figures_involved', None),

        # OTHER
        circuits=kwargs.get('circuits', None)
    )


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
            upper_date='2017-01-31',
            lower_date='2017-01-01',
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
            upper_date=target_date.isoformat(),
            lower_date='2017-01-01',
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_date_range_unbounded_below(self):
        """should filter by date range - unbounded below."""
        incident1 = IncidentPageFactory(date=date(2017, 1, 15))
        incident2 = IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 2, 1))

        summary, incidents = create_incident_filter(
            upper_date='2017-01-31',
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
            lower_date='2017-02-02',
            upper_date='2017-02-28',
        ).fetch()
        self.assertEqual(len(incidents), 0)

    def test_should_filter_by_date_range_unbounded_above(self):
        """should filter by date range - unbounded above"""
        incident1 = IncidentPageFactory(date=date(2017, 1, 15))
        IncidentPageFactory(date=date(2016, 12, 31))
        incident2 = IncidentPageFactory(date=date(2017, 2, 1))

        summary, incidents = create_incident_filter(
            lower_date='2017-01-01',
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


class ChoiceFilters(TestCase):
    def setUp(self):
        self.custody = 'CUSTODY'
        self.returned_full = 'RETURNED_FULL'
        self.unknown = 'UNKNOWN'

    def test_should_filter_by_choice_field(self):
        """should filter via a field that is a choice field"""

        target = IncidentPageFactory(
            status_of_seized_equipment=self.custody
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.returned_full
        )
        summary, incidents = create_incident_filter(
            status_of_seized_equipment=self.custody
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_filter_should_return_all_if_choice_field_invalid(self):
        """should not filter if choice is invalid"""

        IncidentPageFactory(
            status_of_seized_equipment=self.custody
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.returned_full
        )
        IncidentPageFactory(
            affiliation='other'
        )
        summary, incidents = create_incident_filter(
            status_of_seized_equipment="hello"
        ).fetch()

        self.assertEqual(len(incidents), 3)

    def test_filter_should_handle_multiple_choices(self):
        """should handle multiple choices"""
        target1 = IncidentPageFactory(
            status_of_seized_equipment=self.custody
        )
        target2 = IncidentPageFactory(
            status_of_seized_equipment=self.returned_full
        )
        IncidentPageFactory(
            status_of_seized_equipment=self.unknown
        )

        summary, incidents = create_incident_filter(
            status_of_seized_equipment='{0},{1}'.format(self.custody, self.returned_full)
        ).fetch()

        self.assertEqual(len(incidents), 2)
        self.assertTrue(target1 in incidents)
        self.assertTrue(target2 in incidents)


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
        fields_to_skip = {'detention_date', 'release_date'}

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
            lower_date='2011-01-01',
            upper_date='2012-01-01',
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
        filters.fetch()


class TestDateFilters(TestCase):
    """Date filters"""
    def setUp(self):
        self.lower_date = date(2017, 2, 12)
        self.upper_date = date(2017, 2, 13)

    def test_should_filter_by_lower_date_inclusive(self):
        """should filter by lower date"""
        target = IncidentPageFactory(
            release_date=self.lower_date
        )

        # This incident should not be included in the filer, because it is before the lower date
        IncidentPageFactory(
            release_date=(self.lower_date - timedelta(days=1))
        )

        summary, incidents = create_incident_filter(
            release_date_lower=self.lower_date.isoformat()
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_upper_date_inclusive(self):
        """should filter by upper date"""
        target = IncidentPageFactory(
            release_date=self.upper_date
        )

        # This incident should not be included in the filer, because it is after the upper date
        IncidentPageFactory(
            release_date=(self.upper_date + timedelta(days=1))
        )

        summary, incidents = create_incident_filter(
            release_date_upper=self.upper_date.isoformat()
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_date_range_inclusive(self):
        """should filter by date range"""
        target1 = IncidentPageFactory(
            release_date=self.upper_date
        )

        target2 = IncidentPageFactory(
            release_date=(self.upper_date)
        )

        # Incidents below and above the filters
        IncidentPageFactory(
            release_date=(self.lower_date - timedelta(days=1))
        )
        IncidentPageFactory(
            release_date=(self.upper_date + timedelta(days=1))
        )

        summary, incidents = create_incident_filter(
            release_date_lower=self.lower_date.isoformat(),
            release_date_upper=self.upper_date.isoformat()
        ).fetch()

        self.assertEqual(len(incidents), 2)
        self.assertTrue(target1 in incidents)
        self.assertTrue(target2 in incidents)

    def test_should_filter_correctly_with_equal_dates(self):
        """should filter correctly if upper and lower dates are equal"""
        target = IncidentPageFactory(
            release_date=self.lower_date
        )

        # This incident should not be included in the filer, because it is before the lower date
        IncidentPageFactory(
            release_date=(self.lower_date - timedelta(days=1))
        )
        IncidentPageFactory(
            release_date=(self.lower_date + timedelta(days=1))
        )

        summary, incidents = create_incident_filter(
            release_date_lower=self.lower_date.isoformat(),
            release_date_upper=self.lower_date.isoformat()
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)
