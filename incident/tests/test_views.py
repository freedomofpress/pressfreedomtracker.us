from django.test import TestCase
from django.contrib.auth import get_user_model
from incident.models import Target, Charge, Nationality, PoliticianOrPublic, Venue
from incident.wagtail_hooks import TargetAdmin, ChargeAdmin, NationalityAdmin, VenueAdmin, PoliticianOrPublicAdmin
from incident.tests.factories import IncidentPageFactory
import json
from datetime import datetime

User = get_user_model()

class TargetMergeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.inc1 = IncidentPageFactory(targets=1, targets_whose_communications_were_obtained=1)
        cls.inc2 = IncidentPageFactory(targets=1, targets_whose_communications_were_obtained=1)
        cls.inc3 = IncidentPageFactory(targets=1, targets_whose_communications_were_obtained=1)
        cls.target1 = cls.inc1.targets.all()[0]
        cls.target2 = cls.inc2.targets.all()[0]
        cls.target3 = cls.inc1.targets_whose_communications_were_obtained.all()[0]
        cls.target4 = cls.inc2.targets_whose_communications_were_obtained.all()[0]
        cls.unincluded_target1 = cls.inc3.targets.all()[0]
        cls.unincluded_target2 = cls.inc3.targets_whose_communications_were_obtained.all()[0]
        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.new_target_title = 'LittleWeaver'
        self.response = self.client.post(
            TargetAdmin().url_helper.merge_url,
            {
                'models_to_merge': json.dumps([{
                    'label': self.target1.title,
                    'id': self.target1.id
                }, {
                    'label': self.target2.title,
                    'id': self.target2.id
                }, {
                    'label': self.target3.title,
                    'id': self.target3.id
                }, {
                    'label': self.target4.title,
                    'id': self.target4.id
                }]),
                'title_for_merged_models': self.new_target_title
            }
        )

    def test_successful_request_redirects(self):
        self.assertEqual(self.response.status_code, 302)

    def test_correct_redirect_url(self):
        """Should redirect to the modelAdmin's index page"""
        self.assertEqual(self.response['location'], TargetAdmin().url_helper.index_url)

    def test_new_target_created(self):
        Target.objects.get(title=self.new_target_title)

    def test_new_target_has_old_target_relationships(self):
        new_target = Target.objects.get(title=self.new_target_title)
        self.assertEqual(set(new_target.targets_incidents.all()), {self.inc1, self.inc2})

    def test_new_target_has_old_target_relationships2(self):
        new_target = Target.objects.get(title=self.new_target_title)
        self.assertEqual(set(new_target.targets_communications_obtained_incidents.all()), {self.inc1, self.inc2})

    def test_merged_targets_are_deleted(self):
        with self.assertRaises(Target.DoesNotExist):
            Target.objects.get(id=self.target1.id)
        with self.assertRaises(Target.DoesNotExist):
            Target.objects.get(id=self.target2.id)


class ChargeMergeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.inc1 = IncidentPageFactory(current_charges=1, dropped_charges=1)
        cls.inc2 = IncidentPageFactory(current_charges=1, dropped_charges=1)
        IncidentPageFactory(current_charges=1, dropped_charges=1)
        cls.charge1 = cls.inc1.current_charges.all()[0]
        cls.charge2 = cls.inc2.current_charges.all()[0]
        cls.charge3 = cls.inc1.dropped_charges.all()[0]
        cls.charge4 = cls.inc2.dropped_charges.all()[0]
        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.new_charge_title = 'Breaking and entering'
        self.response = self.client.post(
            ChargeAdmin().url_helper.merge_url,
            {
                'models_to_merge': json.dumps([{
                    'label': self.charge1.title,
                    'id': self.charge1.id
                }, {
                    'label': self.charge2.title,
                    'id': self.charge2.id
                }, {
                    'label': self.charge3.title,
                    'id': self.charge3.id
                }, {
                    'label': self.charge4.title,
                    'id': self.charge4.id
                }]),
                'title_for_merged_models': self.new_charge_title
            }
        )

    def test_successful_request_redirects(self):
        self.assertEqual(self.response.status_code, 302)

    def test_correct_redirect_url(self):
        """Should redirect to the modelAdmin's index page"""
        self.assertEqual(self.response['location'], ChargeAdmin().url_helper.index_url)

    def test_new_charge_created(self):
        Charge.objects.get(title=self.new_charge_title)

    def test_new_charge_has_old_charge_relationships(self):
        new_charge = Charge.objects.get(title=self.new_charge_title)
        self.assertEqual(set(new_charge.current_charge_incidents.all()), {self.inc1, self.inc2})

    def test_new_charge_has_old_charge_relationships2(self):
        new_charge = Charge.objects.get(title=self.new_charge_title)
        self.assertEqual(set(new_charge.dropped_charge_incidents.all()), {self.inc1, self.inc2})

    def test_merged_charges_are_deleted(self):
        with self.assertRaises(Charge.DoesNotExist):
            Charge.objects.get(id=self.charge1.id)
        with self.assertRaises(Charge.DoesNotExist):
            Charge.objects.get(id=self.charge2.id)


class NationalityMergeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.inc1 = IncidentPageFactory(target_nationality=1)
        cls.inc2 = IncidentPageFactory(target_nationality=1)
        cls.nation1 = cls.inc1.target_nationality.all()[0]
        cls.nation2 = cls.inc2.target_nationality.all()[0]
        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.new_nation_title = 'Canadiran'
        self.response = self.client.post(
            NationalityAdmin().url_helper.merge_url,
            {
                'models_to_merge': json.dumps([{
                    'label': self.nation1.title,
                    'id': self.nation1.id
                }, {
                    'label': self.nation2.title,
                    'id': self.nation2.id
                }]),
                'title_for_merged_models': self.new_nation_title
            }
        )

    def test_successful_request_redirects(self):
        self.assertEqual(self.response.status_code, 302)

    def test_correct_redirect_url(self):
        """Should redirect to the modelAdmin's index page"""
        self.assertEqual(self.response['location'], NationalityAdmin().url_helper.index_url)

    def test_new_nation_created(self):
        Nationality.objects.get(title=self.new_nation_title)

    def test_new_nation_has_old_nation_relationships(self):
        new_nation = Nationality.objects.get(title=self.new_nation_title)
        self.assertEqual(set(new_nation.nationality_incidents.all()), {self.inc1, self.inc2})

    def test_merged_nations_are_deleted(self):
        with self.assertRaises(Nationality.DoesNotExist):
            Nationality.objects.get(id=self.nation1.id)
        with self.assertRaises(Nationality.DoesNotExist):
            Nationality.objects.get(id=self.nation2.id)


class VenueMergeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.venue1 = Venue.objects.create(title='Canada')
        cls.venue2 = Venue.objects.create(title='Iran')
        cls.inc1 = IncidentPageFactory(venue=[cls.venue1.id])
        cls.inc2 = IncidentPageFactory(venue=[cls.venue2.id])
        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.new_venue_title = 'Canadiran'
        self.response = self.client.post(
            VenueAdmin().url_helper.merge_url,
            {
                'models_to_merge': json.dumps([{
                    'label': self.venue1.title,
                    'id': self.venue1.id
                }, {
                    'label': self.venue2.title,
                    'id': self.venue2.id
                }]),
                'title_for_merged_models': self.new_venue_title
            }
        )

    def test_successful_request_redirects(self):
        self.assertEqual(self.response.status_code, 302)

    def test_correct_redirect_url(self):
        """Should redirect to the modelAdmin's index page"""
        self.assertEqual(self.response['location'], VenueAdmin().url_helper.index_url)

    def test_new_venue_created(self):
        Venue.objects.get(title=self.new_venue_title)

    def test_new_venue_has_old_venue_relationships(self):
        new_venue = Venue.objects.get(title=self.new_venue_title)
        self.assertEqual(set(new_venue.venue_incidents.all()), {self.inc1, self.inc2})

    def test_merged_venues_are_deleted(self):
        with self.assertRaises(Venue.DoesNotExist):
            Venue.objects.get(id=self.venue1.id)
        with self.assertRaises(Venue.DoesNotExist):
            Venue.objects.get(id=self.venue2.id)


class PoliticianOrPublicMergeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.inc1 = IncidentPageFactory(politicians_or_public_figures_involved=1)
        cls.inc2 = IncidentPageFactory(politicians_or_public_figures_involved=1)
        # Ensures that unintended incidents are not included
        IncidentPageFactory(politicians_or_public_figures_involved=1)
        cls.pop1 = cls.inc1.politicians_or_public_figures_involved.all()[0]
        cls.pop2 = cls.inc2.politicians_or_public_figures_involved.all()[0]
        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.new_pop_title = 'LittleWeaver'
        self.response = self.client.post(
            PoliticianOrPublicAdmin().url_helper.merge_url,
            {
                'models_to_merge': json.dumps([{
                    'label': self.pop1.title,
                    'id': self.pop1.id
                }, {
                    'label': self.pop2.title,
                    'id': self.pop2.id
                }]),
                'title_for_merged_models': self.new_pop_title
            }
        )

    def test_pops_only_have_one_m2m(self):
        """If PoliticianOrPublics have more than one related_object, data will be lost on merge"""
        self.assertEqual(len(PoliticianOrPublic._meta.related_objects), 1)

    def test_successful_request_redirects(self):
        self.assertEqual(self.response.status_code, 302)

    def test_correct_redirect_url(self):
        """Should redirect to the modelAdmin's index page"""
        self.assertEqual(self.response['location'], PoliticianOrPublicAdmin().url_helper.index_url)

    def test_new_pop_created(self):
        PoliticianOrPublic.objects.get(title=self.new_pop_title)

    def test_new_pop_has_old_pop_relationships(self):
        new_pop = PoliticianOrPublic.objects.get(title=self.new_pop_title)
        self.assertEqual(set(new_pop.politicians_or_public_incidents.all()), {self.inc1, self.inc2})

    def test_merged_pops_are_deleted(self):
        with self.assertRaises(PoliticianOrPublic.DoesNotExist):
            PoliticianOrPublic.objects.get(id=self.pop1.id)
        with self.assertRaises(PoliticianOrPublic.DoesNotExist):
            PoliticianOrPublic.objects.get(id=self.pop2.id)
