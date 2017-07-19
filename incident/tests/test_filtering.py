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


class TestFiltering(TestCase):
    """Incident filters"""
    def setUp(self):
        self.index = IncidentIndexPageFactory()

    def test_should_filter_by_date_range(self):
        """should filter by date range."""
        target = IncidentPageFactory(date=date(2017, 1, 15))
        IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 2, 1))

        incidents = IncidentFilter(
            search_text=None,
            categories=None,
            upper_date='2017-01-31',
            lower_date='2017-01-01',
            targets=None,
            affiliation=None,
            city=None,
            state=None,
            tags=None,
            # ARREST/DETENTION
            arrest_status=None,
            status_of_charges=None,
            current_charges=None,
            dropped_charges=None,
            detention_date_upper=None,
            detention_date_lower=None,
            release_date_upper=None,
            release_date_lower=None,
            unnecessary_use_of_force=None,
            # LAWSUIT
            lawsuit_name=None,
            venue=None,
            # EQUIPMENT
            equipment_seized=None,
            equipment_broken=None,
            status_of_seized_equipment=None,
            is_search_warrant_obtained=None,
            actor=None,
            # BORDER STOP
            border_point=None,
            stopped_at_border=None,
            stopped_previously=None,
            target_us_citizenship_status=None,
            denial_of_entry=None,
            target_nationality=None,
            did_authorities_ask_for_device_access=None,
            did_authorities_ask_for_social_media_user=None,
            did_authorities_ask_for_social_media_pass=None,
            did_authorities_ask_about_work=None,
            were_devices_searched_or_seized=None,
            # PHYSICAL ASSAULT
            assailant=None,
            was_journalist_targeted=None,
            # LEAK PROSECUTION
            charged_under_espionage_act=None,
            # SUBPOENA
            subpoena_subject=None,
            subpoena_type=None,
            subpoena_status=None,
            held_in_contempt=None,
            detention_status=None,
            # LEGAL ORDER
            third_party_in_possession_of_communications=None,
            third_party_business=None,
            legal_order_type=None,
            # PRIOR RESTRAINT
            status_of_prior_restraint=None,
            # DENIAL OF ACCESS
            politicians_or_public_figures_involved=None,
            # OTHER
            circuits=None
        ).fetch()

        self.assertEqual({target}, set(incidents))

    def test_filter_by_date_range_should_be_incluve_on_upper_date(self):
        target_date = date(2017, 2, 12)
        target = IncidentPageFactory(date=target_date)
        IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 4, 1))

        incidents = IncidentFilter(
            search_text=None,
            categories=None,
            upper_date=target_date.isoformat(),
            lower_date='2017-01-01',
            targets=None,
            affiliation=None,
            city=None,
            state=None,
            tags=None,
            # ARREST/DETENTION
            arrest_status=None,
            status_of_charges=None,
            current_charges=None,
            dropped_charges=None,
            detention_date_upper=None,
            detention_date_lower=None,
            release_date_upper=None,
            release_date_lower=None,
            unnecessary_use_of_force=None,
            # LAWSUIT
            lawsuit_name=None,
            venue=None,
            # EQUIPMENT
            equipment_seized=None,
            equipment_broken=None,
            status_of_seized_equipment=None,
            is_search_warrant_obtained=None,
            actor=None,
            # BORDER STOP
            border_point=None,
            stopped_at_border=None,
            stopped_previously=None,
            target_us_citizenship_status=None,
            denial_of_entry=None,
            target_nationality=None,
            did_authorities_ask_for_device_access=None,
            did_authorities_ask_for_social_media_user=None,
            did_authorities_ask_for_social_media_pass=None,
            did_authorities_ask_about_work=None,
            were_devices_searched_or_seized=None,
            # PHYSICAL ASSAULT
            assailant=None,
            was_journalist_targeted=None,
            # LEAK PROSECUTION
            charged_under_espionage_act=None,
            # SUBPOENA
            subpoena_subject=None,
            subpoena_type=None,
            subpoena_status=None,
            held_in_contempt=None,
            detention_status=None,
            # LEGAL ORDER
            third_party_in_possession_of_communications=None,
            third_party_business=None,
            legal_order_type=None,
            # PRIOR RESTRAINT
            status_of_prior_restraint=None,
            # DENIAL OF ACCESS
            politicians_or_public_figures_involved=None,
            # OTHER
            circuits=None
        ).fetch()

        self.assertEqual({target}, set(incidents))

    def test_should_filter_by_date_range_unbounded_below(self):
        """should filter by date range - unbounded below."""
        incident1 = IncidentPageFactory(date=date(2017, 1, 15))
        incident2 = IncidentPageFactory(date=date(2016, 12, 31))
        IncidentPageFactory(date=date(2017, 2, 1))

        incidents = IncidentFilter(
            search_text=None,
            categories=None,
            upper_date='2017-01-31',
            lower_date=None,
            targets=None,
            affiliation=None,
            city=None,
            state=None,
            tags=None,
            # ARREST/DETENTION
            arrest_status=None,
            status_of_charges=None,
            current_charges=None,
            dropped_charges=None,
            detention_date_upper=None,
            detention_date_lower=None,
            release_date_upper=None,
            release_date_lower=None,
            unnecessary_use_of_force=None,
            # LAWSUIT
            lawsuit_name=None,
            venue=None,
            # EQUIPMENT
            equipment_seized=None,
            equipment_broken=None,
            status_of_seized_equipment=None,
            is_search_warrant_obtained=None,
            actor=None,
            # BORDER STOP
            border_point=None,
            stopped_at_border=None,
            stopped_previously=None,
            target_us_citizenship_status=None,
            denial_of_entry=None,
            target_nationality=None,
            did_authorities_ask_for_device_access=None,
            did_authorities_ask_for_social_media_user=None,
            did_authorities_ask_for_social_media_pass=None,
            did_authorities_ask_about_work=None,
            were_devices_searched_or_seized=None,
            # PHYSICAL ASSAULT
            assailant=None,
            was_journalist_targeted=None,
            # LEAK PROSECUTION
            charged_under_espionage_act=None,
            # SUBPOENA
            subpoena_subject=None,
            subpoena_type=None,
            subpoena_status=None,
            held_in_contempt=None,
            detention_status=None,
            # LEGAL ORDER
            third_party_in_possession_of_communications=None,
            third_party_business=None,
            legal_order_type=None,
            # PRIOR RESTRAINT
            status_of_prior_restraint=None,
            # DENIAL OF ACCESS
            politicians_or_public_figures_involved=None,
            # OTHER
            circuits=None
        ).fetch()

        self.assertEqual({incident2, incident1}, set(incidents))

    def test_should_filter_by_date_range_unbounded_above(self):
        """should filter by date range - unbounded above"""
        incident1 = IncidentPageFactory(date=date(2017, 1, 15))
        IncidentPageFactory(date=date(2016, 12, 31))
        incident2 = IncidentPageFactory(date=date(2017, 2, 1))

        incidents = IncidentFilter(
            search_text=None,
            categories=None,
            upper_date=None,
            lower_date='2017-01-01',
            targets=None,
            affiliation=None,
            city=None,
            state=None,
            tags=None,
            # ARREST/DETENTION
            arrest_status=None,
            status_of_charges=None,
            current_charges=None,
            dropped_charges=None,
            detention_date_upper=None,
            detention_date_lower=None,
            release_date_upper=None,
            release_date_lower=None,
            unnecessary_use_of_force=None,
            # LAWSUIT
            lawsuit_name=None,
            venue=None,
            # EQUIPMENT
            equipment_seized=None,
            equipment_broken=None,
            status_of_seized_equipment=None,
            is_search_warrant_obtained=None,
            actor=None,
            # BORDER STOP
            border_point=None,
            stopped_at_border=None,
            stopped_previously=None,
            target_us_citizenship_status=None,
            denial_of_entry=None,
            target_nationality=None,
            did_authorities_ask_for_device_access=None,
            did_authorities_ask_for_social_media_user=None,
            did_authorities_ask_for_social_media_pass=None,
            did_authorities_ask_about_work=None,
            were_devices_searched_or_seized=None,
            # PHYSICAL ASSAULT
            assailant=None,
            was_journalist_targeted=None,
            # LEAK PROSECUTION
            charged_under_espionage_act=None,
            # SUBPOENA
            subpoena_subject=None,
            subpoena_type=None,
            subpoena_status=None,
            held_in_contempt=None,
            detention_status=None,
            # LEGAL ORDER
            third_party_in_possession_of_communications=None,
            third_party_business=None,
            legal_order_type=None,
            # PRIOR RESTRAINT
            status_of_prior_restraint=None,
            # DENIAL OF ACCESS
            politicians_or_public_figures_involved=None,
            # OTHER
            circuits=None
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

        incidents = IncidentFilter(
            search_text='eggplant',
            categories=None,
            upper_date=None,
            lower_date=None,
            targets=None,
            affiliation=None,
            city=None,
            state=None,
            tags=None,
            # ARREST/DETENTION
            arrest_status=None,
            status_of_charges=None,
            current_charges=None,
            dropped_charges=None,
            detention_date_upper=None,
            detention_date_lower=None,
            release_date_upper=None,
            release_date_lower=None,
            unnecessary_use_of_force=None,
            # LAWSUIT
            lawsuit_name=None,
            venue=None,
            # EQUIPMENT
            equipment_seized=None,
            equipment_broken=None,
            status_of_seized_equipment=None,
            is_search_warrant_obtained=None,
            actor=None,
            # BORDER STOP
            border_point=None,
            stopped_at_border=None,
            stopped_previously=None,
            target_us_citizenship_status=None,
            denial_of_entry=None,
            target_nationality=None,
            did_authorities_ask_for_device_access=None,
            did_authorities_ask_for_social_media_user=None,
            did_authorities_ask_for_social_media_pass=None,
            did_authorities_ask_about_work=None,
            were_devices_searched_or_seized=None,
            # PHYSICAL ASSAULT
            assailant=None,
            was_journalist_targeted=None,
            # LEAK PROSECUTION
            charged_under_espionage_act=None,
            # SUBPOENA
            subpoena_subject=None,
            subpoena_type=None,
            subpoena_status=None,
            held_in_contempt=None,
            detention_status=None,
            # LEGAL ORDER
            third_party_in_possession_of_communications=None,
            third_party_business=None,
            legal_order_type=None,
            # PRIOR RESTRAINT
            status_of_prior_restraint=None,
            # DENIAL OF ACCESS
            politicians_or_public_figures_involved=None,
            # OTHER
            circuits=None
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
        incidents = IncidentFilter(
            search_text=None,
            categories=str(category1.id),
            upper_date=None,
            lower_date=None,
            targets=None,
            affiliation=None,
            city=None,
            state=None,
            tags=None,
            # ARREST/DETENTION
            arrest_status=None,
            status_of_charges=None,
            current_charges=None,
            dropped_charges=None,
            detention_date_upper=None,
            detention_date_lower=None,
            release_date_upper=None,
            release_date_lower=None,
            unnecessary_use_of_force=None,
            # LAWSUIT
            lawsuit_name=None,
            venue=None,
            # EQUIPMENT
            equipment_seized=None,
            equipment_broken=None,
            status_of_seized_equipment=None,
            is_search_warrant_obtained=None,
            actor=None,
            # BORDER STOP
            border_point=None,
            stopped_at_border=None,
            stopped_previously=None,
            target_us_citizenship_status=None,
            denial_of_entry=None,
            target_nationality=None,
            did_authorities_ask_for_device_access=None,
            did_authorities_ask_for_social_media_user=None,
            did_authorities_ask_for_social_media_pass=None,
            did_authorities_ask_about_work=None,
            were_devices_searched_or_seized=None,
            # PHYSICAL ASSAULT
            assailant=None,
            was_journalist_targeted=None,
            # LEAK PROSECUTION
            charged_under_espionage_act=None,
            # SUBPOENA
            subpoena_subject=None,
            subpoena_type=None,
            subpoena_status=None,
            held_in_contempt=None,
            detention_status=None,
            # LEGAL ORDER
            third_party_in_possession_of_communications=None,
            third_party_business=None,
            legal_order_type=None,
            # PRIOR RESTRAINT
            status_of_prior_restraint=None,
            # DENIAL OF ACCESS
            politicians_or_public_figures_involved=None,
            # OTHER
            circuits=None
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
        incidents = IncidentFilter(
            search_text=None,
            categories='{0},{1}'.format(str(category2.id), str(category3.id)),
            upper_date=None,
            lower_date=None,
            targets=None,
            affiliation=None,
            city=None,
            state=None,
            tags=None,
            # ARREST/DETENTION
            arrest_status=None,
            status_of_charges=None,
            current_charges=None,
            dropped_charges=None,
            detention_date_upper=None,
            detention_date_lower=None,
            release_date_upper=None,
            release_date_lower=None,
            unnecessary_use_of_force=None,
            # LAWSUIT
            lawsuit_name=None,
            venue=None,
            # EQUIPMENT
            equipment_seized=None,
            equipment_broken=None,
            status_of_seized_equipment=None,
            is_search_warrant_obtained=None,
            actor=None,
            # BORDER STOP
            border_point=None,
            stopped_at_border=None,
            stopped_previously=None,
            target_us_citizenship_status=None,
            denial_of_entry=None,
            target_nationality=None,
            did_authorities_ask_for_device_access=None,
            did_authorities_ask_for_social_media_user=None,
            did_authorities_ask_for_social_media_pass=None,
            did_authorities_ask_about_work=None,
            were_devices_searched_or_seized=None,
            # PHYSICAL ASSAULT
            assailant=None,
            was_journalist_targeted=None,
            # LEAK PROSECUTION
            charged_under_espionage_act=None,
            # SUBPOENA
            subpoena_subject=None,
            subpoena_type=None,
            subpoena_status=None,
            held_in_contempt=None,
            detention_status=None,
            # LEGAL ORDER
            third_party_in_possession_of_communications=None,
            third_party_business=None,
            legal_order_type=None,
            # PRIOR RESTRAINT
            status_of_prior_restraint=None,
            # DENIAL OF ACCESS
            politicians_or_public_figures_involved=None,
            # OTHER
            circuits=None
        ).fetch()
        self.assertEqual({incident1, incident2}, set(incidents))

    def should_xyz(self):
        self.assertTrue(False)
