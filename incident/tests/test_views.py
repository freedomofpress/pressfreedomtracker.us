import json

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from wagtail.core.models import Site
from wagtail.core.rich_text import RichText

from incident.models import Target, Charge, Nationality, PoliticianOrPublic, Venue, Journalist, Institution, TargetedJournalist
from incident.wagtail_hooks import TargetAdmin, ChargeAdmin, NationalityAdmin, VenueAdmin, PoliticianOrPublicAdmin, JournalistAdmin, InstitutionAdmin
from incident.tests.factories import (
    IncidentPageFactory,
    IncidentIndexPageFactory,
    TargetedJournalistFactory,
)


User = get_user_model()


class IncidentAdminSearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.get(is_default_site=True)

        incident_index_page = IncidentIndexPageFactory(
            parent=site.root_page,
        )

        cls.incident_page1 = IncidentPageFactory(
            parent=incident_index_page,
            title='asdf',
        )
        cls.incident_page2 = IncidentPageFactory(
            parent=incident_index_page,
            title='zxcv',
        )
        cls.incident_page3 = IncidentPageFactory(
            parent=incident_index_page,
            title='qwerty',
            body=[('rich_text', RichText('<p>asdf</p>'))],
        )
        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.url = reverse('incident-admin-search')

    def test_search_title(self):
        response = self.client.get(self.url, {'q': 'zxcv'})
        self.assertEqual(set(response.context['pages']), {self.incident_page2})

    def test_search_title_and_body(self):
        response = self.client.get(self.url, {'q': 'asdf'})
        self.assertEqual(
            set(response.context['pages']),
            {self.incident_page1, self.incident_page3},
        )


class InstitutionMergeViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.inc1 = IncidentPageFactory(institution_targets=1)
        cls.inc2 = IncidentPageFactory(institution_targets=2)
        cls.inc3 = IncidentPageFactory(institution_targets=3)

        cls.tj = TargetedJournalistFactory(institution=cls.inc1.targeted_institutions.first())

        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.new_institution_title = 'Insitution XIII'

        inst1 = self.inc1.targeted_institutions.first()
        inst2, inst3 = self.inc2.targeted_institutions.all()
        inst4 = self.inc3.targeted_institutions.first()

        self.response = self.client.post(
            InstitutionAdmin().url_helper.merge_url,
            {
                'models_to_merge': json.dumps([{
                    'label': inst1.title,
                    'pk': inst1.pk,
                }, {
                    'label': inst2.title,
                    'pk': inst2.pk,
                }, {
                    'label': inst3.title,
                    'pk': inst3.pk,
                }, {
                    'label': inst4.title,
                    'pk': inst4.pk,
                },
                ]),
                'title_for_merged_models': self.new_institution_title
            }
        )

    def test_successful_request_redirects(self):
        self.assertEqual(self.response.status_code, 302)

    def test_correct_redirect_url(self):
        """Should redirect to the modelAdmin's index page"""
        self.assertEqual(self.response['location'], InstitutionAdmin().url_helper.index_url)

    def test_new_institution_should_be_created(self):
        institution = Institution.objects.get(title=self.new_institution_title)

        self.assertEqual(
            set(institution.institutions_incidents.all()),
            {self.inc1, self.inc2, self.inc3}
        )

    def test_targeted_journalists_at_institutions_should_be_updated(self):
        self.assertEqual(
            TargetedJournalist.objects.get(pk=self.tj.pk).institution,
            Institution.objects.get(title=self.new_institution_title)
        )


class JournalistMergeViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tj1 = TargetedJournalistFactory()
        cls.tj2 = TargetedJournalistFactory()
        cls.tj3 = TargetedJournalistFactory()
        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.new_journalist_title = 'Person One'
        self.response = self.client.post(
            JournalistAdmin().url_helper.merge_url,
            {
                'models_to_merge': json.dumps([{
                    'label': self.tj1.journalist.title,
                    'pk': self.tj1.journalist.pk
                }, {
                    'label': self.tj2.journalist.title,
                    'pk': self.tj2.journalist.pk
                }, {
                    'label': self.tj3.journalist.title,
                    'pk': self.tj3.journalist.pk
                },
                ]),
                'title_for_merged_models': self.new_journalist_title
            }
        )

    def test_successful_request_redirects(self):
        self.assertEqual(self.response.status_code, 302)

    def test_correct_redirect_url(self):
        """Should redirect to the modelAdmin's index page"""
        self.assertEqual(self.response['location'], JournalistAdmin().url_helper.index_url)

    def test_new_journalist_should_be_created(self):
        journalist = Journalist.objects.get(title=self.new_journalist_title)

        self.assertEqual(
            set(journalist.targeted_incidents.all()),
            {self.tj1, self.tj2, self.tj3}
        )


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
                    'pk': self.target1.pk
                }, {
                    'label': self.target2.title,
                    'pk': self.target2.pk
                }, {
                    'label': self.target3.title,
                    'pk': self.target3.pk
                }, {
                    'label': self.target4.title,
                    'pk': self.target4.pk
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
            Target.objects.get(pk=self.target1.pk)
        with self.assertRaises(Target.DoesNotExist):
            Target.objects.get(pk=self.target2.pk)


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
                    'pk': self.charge1.pk
                }, {
                    'label': self.charge2.title,
                    'pk': self.charge2.pk
                }, {
                    'label': self.charge3.title,
                    'pk': self.charge3.pk
                }, {
                    'label': self.charge4.title,
                    'pk': self.charge4.pk
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
            Charge.objects.get(pk=self.charge1.pk)
        with self.assertRaises(Charge.DoesNotExist):
            Charge.objects.get(pk=self.charge2.pk)


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
                    'pk': self.nation1.pk
                }, {
                    'label': self.nation2.title,
                    'pk': self.nation2.pk
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
            Nationality.objects.get(pk=self.nation1.pk)
        with self.assertRaises(Nationality.DoesNotExist):
            Nationality.objects.get(pk=self.nation2.pk)


class VenueMergeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.venue1 = Venue.objects.create(title='Canada')
        cls.venue2 = Venue.objects.create(title='Iran')
        cls.inc1 = IncidentPageFactory()
        cls.inc1.venue.add(cls.venue1)
        cls.inc1.save()
        cls.inc2 = IncidentPageFactory()
        cls.inc2.venue.add(cls.venue2)
        cls.inc2.save()
        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.new_venue_title = 'Canadiran'
        self.response = self.client.post(
            VenueAdmin().url_helper.merge_url,
            {
                'models_to_merge': json.dumps([{
                    'label': self.venue1.title,
                    'pk': self.venue1.pk
                }, {
                    'label': self.venue2.title,
                    'pk': self.venue2.pk
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
            Venue.objects.get(pk=self.venue1.pk)
        with self.assertRaises(Venue.DoesNotExist):
            Venue.objects.get(pk=self.venue2.pk)


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
                    'pk': self.pop1.pk
                }, {
                    'label': self.pop2.title,
                    'pk': self.pop2.pk
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
            PoliticianOrPublic.objects.get(pk=self.pop1.pk)
        with self.assertRaises(PoliticianOrPublic.DoesNotExist):
            PoliticianOrPublic.objects.get(pk=self.pop2.pk)
