from datetime import date

from django.test import TestCase
from wagtail.wagtailcore.rich_text import RichText

from incident.tests.factories import (
    IncidentPageFactory,
    IncidentIndexPageFactory,
    IncidentCategorizationFactory,
)
from common.tests.factories import CategoryPageFactory
from incident.utils.incident_filter import IncidentFilter


def CreateIncidentFilter(**kwargs):
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
        subpoena_subject=kwargs.get('subpoena_subject', None),
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

        summary, incidents = CreateIncidentFilter(
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

        summary, incidents =  CreateIncidentFilter(
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

        summary, incidents = CreateIncidentFilter(
            upper_date='2017-01-31',
        ).fetch()

        self.assertEqual({incident2, incident1}, set(incidents))

    def test_should_filter_by_date_range_unbounded_above(self):
        """should filter by date range - unbounded above"""
        incident1 = IncidentPageFactory(date=date(2017, 1, 15))
        IncidentPageFactory(date=date(2016, 12, 31))
        incident2 = IncidentPageFactory(date=date(2017, 2, 1))

        summary, incidents = CreateIncidentFilter(
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

        summary, incidents = CreateIncidentFilter(
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

        summary, incidents = CreateIncidentFilter(
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

        summary, incidents = CreateIncidentFilter(
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
        incidents = CreateIncidentFilter(
            affiliation=affiliation
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_should_filter_by_choice_field(self):
        """should filter via a field that is a choice field"""
        target_status_of_seized_equipment = 'CUSTODY'
        other_status_of_seized_equipment = 'RETURNED_FULL'

        target = IncidentPageFactory(
            status_of_seized_equipment=target_status_of_seized_equipment
        )
        IncidentPageFactory(
            status_of_seized_equipment=other_status_of_seized_equipment
        )
        incidents = CreateIncidentFilter(
            status_of_seized_equipment=target_status_of_seized_equipment
        ).fetch()

        self.assertEqual(len(incidents), 1)
        self.assertTrue(target in incidents)

    def test_filter_should_return_all_if_choice_field_invalid(self):
        """should not filter if choice is invalid"""
        inc1_status_of_seized_equipment = 'CUSTODY'
        inc2_status_of_seized_equipment = 'RETURNED_FULL'

        IncidentPageFactory(
            status_of_seized_equipment=inc1_status_of_seized_equipment
        )
        IncidentPageFactory(
            status_of_seized_equipment=inc2_status_of_seized_equipment
        )
        IncidentPageFactory(
            affiliation='other'
        )
        incidents = CreateIncidentFilter(
            status_of_seized_equipment="hello"
        ).fetch()

        self.assertEqual(len(incidents), 3)
