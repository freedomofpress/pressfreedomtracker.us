import csv
import io
import json
from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from wagtail.models import Site
from wagtail.rich_text import RichText

from incident.models import Charge, Nationality, PoliticianOrPublic, Venue, Journalist, Institution, TargetedJournalist, GovernmentWorker, IncidentPage, choices
from incident.wagtail_hooks import ChargeAdmin, NationalityAdmin, VenueAdmin, PoliticianOrPublicAdmin, JournalistAdmin, InstitutionAdmin, GovernmentWorkerAdmin
from incident.tests.factories import (
    ChargeFactory,
    IncidentPageFactory,
    IncidentIndexPageFactory,
    TargetedJournalistFactory,
    IncidentChargeFactory,
    IncidentChargeWithUpdatesFactory,
)


User = get_user_model()


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
        cls.inc1 = IncidentPageFactory(workers_whose_communications_were_obtained=1)
        cls.inc2 = IncidentPageFactory(workers_whose_communications_were_obtained=1)
        cls.inc3 = IncidentPageFactory(workers_whose_communications_were_obtained=1)
        cls.worker1 = cls.inc1.workers_whose_communications_were_obtained.first()
        cls.worker2 = cls.inc2.workers_whose_communications_were_obtained.first()
        cls.worker3 = cls.inc3.workers_whose_communications_were_obtained.first()
        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.new_target_title = 'LittleWeaver'

        self.response = self.client.post(
            GovernmentWorkerAdmin().url_helper.merge_url,
            {
                'models_to_merge': json.dumps([{
                    'label': self.worker1.title,
                    'pk': self.worker1.pk
                }, {
                    'label': self.worker2.title,
                    'pk': self.worker2.pk
                }, {
                    'label': self.worker3.title,
                    'pk': self.worker3.pk
                }]),
                'title_for_merged_models': self.new_target_title
            }
        )

    def test_successful_request_redirects(self):
        self.assertEqual(self.response.status_code, 302)

    def test_correct_redirect_url(self):
        """Should redirect to the modelAdmin's index page"""
        self.assertEqual(self.response['location'], GovernmentWorkerAdmin().url_helper.index_url)

    def test_new_target_created(self):
        GovernmentWorker.objects.get(title=self.new_target_title)

    def test_new_target_has_old_target_relationships(self):
        new_worker = GovernmentWorker.objects.get(title=self.new_target_title)
        self.assertEqual(
            set(new_worker.incidents.all()),
            {self.inc1, self.inc2, self.inc3},
        )

    def test_new_target_has_old_target_relationships2(self):
        new_worker = GovernmentWorker.objects.get(title=self.new_target_title)
        self.assertEqual(
            set(new_worker.incidents.all()),
            {self.inc1, self.inc2, self.inc3},
        )

    def test_merged_targets_are_deleted(self):
        with self.assertRaises(GovernmentWorker.DoesNotExist):
            GovernmentWorker.objects.get(pk=self.worker1.pk)
        with self.assertRaises(GovernmentWorker.DoesNotExist):
            GovernmentWorker.objects.get(pk=self.worker2.pk)
        with self.assertRaises(GovernmentWorker.DoesNotExist):
            GovernmentWorker.objects.get(pk=self.worker3.pk)


class ChargeMergeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.inc1 = IncidentPageFactory()
        cls.inc2 = IncidentPageFactory()

        cls.charge1, cls.charge2, cls.charge3, cls.charge4 = ChargeFactory.create_batch(4)
        IncidentChargeFactory(incident_page=cls.inc1, charge=cls.charge1)
        IncidentChargeWithUpdatesFactory(incident_page=cls.inc1, charge=cls.charge2)
        IncidentChargeFactory(incident_page=cls.inc2, charge=cls.charge3)
        IncidentChargeWithUpdatesFactory(incident_page=cls.inc2, charge=cls.charge4)

        IncidentChargeFactory()  # this should not be affected

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
        incidents_with_new_charge = IncidentPage.objects.filter(
            charges__charge__title=self.new_charge_title
        ).distinct()
        self.assertQuerysetEqual(incidents_with_new_charge, [self.inc1, self.inc2])

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


class LegalOrderImportTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            username='test',
            password='test',
            email='test@example.com',
        )
        cls.inc1 = IncidentPageFactory()
        cls.inc2 = IncidentPageFactory()
        cls.inc3 = IncidentPageFactory()

    def setUp(self):
        self.client.force_login(self.user)
        self.import_url = reverse('import_legal_orders:show_form')
        self.confirm_url = reverse('import_legal_orders:confirm')

    def post_csv(self, row_data, *args, **kwargs):
        csv_content = io.StringIO()
        fieldnames = [
            'slug',
            'venue',
            'target',
        ]
        for order_number in range(1, 5):
            fieldnames.extend([
                f'legal_order{order_number}_type',
                f'legal_order{order_number}_information_requested',
            ])
            for status_number in range(1, 5):
                fieldnames.extend([
                    f'legal_order{order_number}_status{status_number}',
                    f'legal_order{order_number}_date{status_number}',
                ])

        writer = csv.DictWriter(csv_content, fieldnames=fieldnames)
        writer.writeheader()
        for row in row_data:
            writer.writerow(row)

        # Reset file pointer for posting
        csv_content.seek(0)
        response = self.client.post(
            path=self.import_url,
            data={'name': 'filename.csv', 'csv_file': csv_content},
            **kwargs,
        )
        return response

    def test_getting_the_form_is_successful(self):
        response = self.client.get(self.import_url)
        self.assertEqual(response.status_code, 200)

    def test_csvs_submitted_with_nonexistent_slugs_are_invalid(self):
        invalid = 'http://localhost:8000/nonexistent-slug'
        response = self.post_csv([{
            'slug': invalid,
        }])
        self.assertContains(
            response,
            f'Row 2, column slug: Could not locate incident at {invalid}'
        )

    def test_csvs_submitted_with_nonexistent_types_are_invalid(self):
        invalid = 'invalid'
        response = self.post_csv([{
            'slug': self.inc1.slug,
            'legal_order1_type': invalid,
        }])
        self.assertContains(
            response,
            f'Row 2, column legal_order1_type: {invalid} is invalid input'
        )

    def test_csvs_submitted_with_nonexistent_information_requested_are_invalid(self):
        invalid = 'invalid'
        response = self.post_csv([{
            'slug': self.inc1.slug,
            'legal_order1_information_requested': invalid,
        }])
        self.assertContains(
            response,
            f'Row 2, column legal_order1_information_requested: {invalid} is invalid input'
        )

    def test_csvs_submitted_with_nonexistent_statuses_are_invalid(self):
        invalid = 'invalid'
        response = self.post_csv([{
            'slug': self.inc1.slug,
            'venue': choices.LegalOrderVenue.STATE.label,
            'target': choices.LegalOrderTarget.JOURNALIST.label,
            'legal_order1_type': choices.LegalOrderType.SUBPOENA.label,
            'legal_order1_information_requested': choices.InformationRequested.OTHER_TESTIMONY.label,
            'legal_order1_status1': invalid,
        }])
        self.assertContains(
            response,
            f'Row 2, column legal_order1_status1: {invalid} is invalid input'
        )

    def test_csvs_submitted_with_invalid_dates_are_invalid(self):
        invalid = '2018-1128'
        response = self.post_csv([{
            'slug': self.inc1.slug,
            'venue': choices.LegalOrderVenue.STATE.label,
            'target': choices.LegalOrderTarget.JOURNALIST.label,
            'legal_order1_type': choices.LegalOrderType.SUBPOENA.label,
            'legal_order1_information_requested': choices.InformationRequested.OTHER_TESTIMONY.label,
            'legal_order1_status1': choices.LegalOrderStatus.PENDING,
            'legal_order1_date1': invalid,
        }])
        self.assertContains(
            response,
            f'Row 2, column legal_order1_date1: Invalid isoformat string: &#x27;{invalid}&#x27;'
        )

    def test_csvs_submitted_with_nonexistent_venues_are_invalid(self):
        invalid = 'invalid'
        response = self.post_csv([{
            'slug': self.inc1.slug,
            'legal_order1_type': choices.LegalOrderType.SUBPOENA.label,
            'venue': invalid,
        }])
        self.assertContains(
            response,
            f'Row 2, column venue: {invalid} is invalid input'
        )

    def test_csvs_submitted_with_nonexistent_targets_are_invalid(self):
        invalid = 'invalid'
        response = self.post_csv([{
            'slug': self.inc1.slug,
            'legal_order1_type': choices.LegalOrderType.SUBPOENA.label,
            'venue': choices.LegalOrderVenue.FEDERAL,
            'target': invalid,
        }])
        self.assertContains(
            response,
            f'Row 2, column target: {invalid} is invalid input'
        )

    def test_posting_a_file_updates_the_session(self):
        venue = choices.LegalOrderVenue.STATE
        target = choices.LegalOrderTarget.JOURNALIST
        order_type = choices.LegalOrderType.SUBPOENA
        info_requested = choices.InformationRequested.OTHER_TESTIMONY
        status1 = choices.LegalOrderStatus.PENDING
        date1 = '2023-01-05'
        status2 = choices.LegalOrderStatus.QUASHED
        date2 = '2023-01-15'
        self.post_csv([{
            'slug': self.inc1.slug,
            'venue': venue.label,
            'target': target.label,
            'legal_order1_type': order_type.label,
            'legal_order1_information_requested': info_requested.label,
            'legal_order1_status1': status1.label,
            'legal_order1_date1': date1,
            'legal_order1_status2': status2.label,
            'legal_order1_date2': date2,
        }], follow=True)

        self.assertEqual(
            self.client.session['legal_order_import'],
            {
                str(self.inc1.pk): {
                    'venue': venue.value,
                    'target': target.value,
                    'legal_orders': [{
                        'information_requested': info_requested.value,
                        'type': order_type.value,
                        'statuses': [{
                            'date': date1,
                            'status': status1.value,
                        }, {
                            'date': date2,
                            'status': status2.value,
                        }],
                    }],
                }
            }
        )

    def test_posting_a_file_with_missing_update_dates_updates_the_session(self):
        venue = choices.LegalOrderVenue.STATE
        target = choices.LegalOrderTarget.JOURNALIST
        order_type = choices.LegalOrderType.SUBPOENA
        info_requested = choices.InformationRequested.OTHER_TESTIMONY
        status1 = choices.LegalOrderStatus.PENDING
        date1 = '2023-01-05'
        status2 = choices.LegalOrderStatus.QUASHED
        date2 = ''
        self.post_csv([{
            'slug': self.inc1.slug,
            'venue': venue.label,
            'target': target.label,
            'legal_order1_type': order_type.label,
            'legal_order1_information_requested': info_requested.label,
            'legal_order1_status1': status1.label,
            'legal_order1_date1': date1,
            'legal_order1_status2': status2.label,
            'legal_order1_date2': date2,
        }], follow=True)

        self.assertEqual(
            self.client.session['legal_order_import'],
            {
                str(self.inc1.pk): {
                    'venue': venue.value,
                    'target': target.value,
                    'legal_orders': [{
                        'information_requested': info_requested.value,
                        'type': order_type.value,
                        'statuses': [{
                            'date': date1,
                            'status': status1.value,
                        }, {
                            'date': None,
                            'status': status2.value,
                        }],
                    }],
                }
            }
        )

    def test_confirming_a_file_a_file_updates_the_incident(self):
        venue = choices.LegalOrderVenue.STATE
        target = choices.LegalOrderTarget.JOURNALIST
        order_type = choices.LegalOrderType.SUBPOENA
        info_requested = choices.InformationRequested.OTHER_TESTIMONY
        status1 = choices.LegalOrderStatus.PENDING
        date1 = date(2023, 1, 5)
        status2 = choices.LegalOrderStatus.QUASHED
        date2 = date(2023, 1, 15)

        session = self.client.session

        session['legal_order_import'] = {
            str(self.inc1.pk): {
                'venue': venue.value,
                'target': target.value,
                'legal_orders': [{
                    'information_requested': info_requested.value,
                    'type': order_type.value,
                    'statuses': [{
                        'date': str(date1),
                        'status': status1.value,
                    }, {
                        'date': str(date2),
                        'status': status2.value,
                    }],
                }],
            }
        }
        session.save()
        response = self.client.post(self.confirm_url)
        self.assertRedirects(
            response,
            reverse('import_legal_orders:show_form'),
        )

        # Successful import removes the corresponding session data
        self.assertNotIn('legal_order_import', self.client.session)

        self.inc1.refresh_from_db()
        self.assertEqual(self.inc1.legal_order_venue, venue)
        self.assertEqual(self.inc1.legal_order_target, target)
        legal_order = self.inc1.legal_orders.all()[0]
        self.assertEqual(legal_order.information_requested, info_requested)
        self.assertEqual(legal_order.order_type, order_type)
        self.assertEqual(legal_order.status, status1)
        self.assertEqual(legal_order.date, date1)
        update = legal_order.updates.all()[0]
        self.assertEqual(update.status, status2)
        self.assertEqual(update.date, date2)

    def test_confirming_a_file_with_missing_update_date_updates_the_incident(self):
        venue = choices.LegalOrderVenue.STATE
        target = choices.LegalOrderTarget.JOURNALIST
        order_type = choices.LegalOrderType.SUBPOENA
        info_requested = choices.InformationRequested.OTHER_TESTIMONY
        status1 = choices.LegalOrderStatus.PENDING
        date1 = date(2023, 1, 5)
        status2 = choices.LegalOrderStatus.QUASHED
        date2 = None

        session = self.client.session

        session['legal_order_import'] = {
            str(self.inc1.pk): {
                'venue': venue.value,
                'target': target.value,
                'legal_orders': [{
                    'information_requested': info_requested.value,
                    'type': order_type.value,
                    'statuses': [{
                        'date': str(date1),
                        'status': status1.value,
                    }, {
                        'date': date2,
                        'status': status2.value,
                    }],
                }],
            }
        }
        session.save()
        response = self.client.post(self.confirm_url)
        self.assertRedirects(
            response,
            reverse('import_legal_orders:show_form'),
        )
        # self.assertEqual(response.status_code, )

        # Successful import removes the corresponding session data
        self.assertNotIn('legal_order_import', self.client.session)

        self.inc1.refresh_from_db()
        self.assertEqual(self.inc1.legal_order_venue, venue)
        self.assertEqual(self.inc1.legal_order_target, target)
        legal_order = self.inc1.legal_orders.all()[0]
        self.assertEqual(legal_order.information_requested, info_requested)
        self.assertEqual(legal_order.order_type, order_type)
        self.assertEqual(legal_order.status, status1)
        self.assertEqual(legal_order.date, date1)
        update = legal_order.updates.all()[0]
        self.assertEqual(update.status, status2)
        self.assertEqual(update.date, date2)
