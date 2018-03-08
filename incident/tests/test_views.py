from django.test import TestCase
from django.contrib.auth import get_user_model
from incident.models import Target, Nationality
from incident.wagtail_hooks import TargetAdmin, NationalityAdmin
from incident.tests.factories import IncidentPageFactory
import json

User = get_user_model()

class TargetMergeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.target1 = Target.objects.create(title='Rachel')
        cls.target2 = Target.objects.create(title='Stephen')
        cls.inc1 = IncidentPageFactory(targets=cls.target1.id)
        cls.inc2 = IncidentPageFactory(targets=cls.target2.id)
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
                }]),
                'title_for_merged_models': self.new_target_title
            }
        )

    def test_targets_only_have_one_m2m(self):
        """If Targets have more than one related_object, data will be lost on merge"""
        self.assertEqual(len(Target._meta.related_objects), 1)

    def test_successful_request_redirects(self):
        self.assertEqual(self.response.status_code, 302)

    def test_correct_redirect_url(self):
        """Should redirect to the modelAdmin's index page"""
        self.assertEqual(self.response['location'], TargetAdmin().url_helper.index_url)

    def test_new_target_created(self):
        Target.objects.get(title=self.new_target_title)

    def test_new_target_has_old_target_relationships(self):
        new_target = Target.objects.get(title=self.new_target_title)
        self.assertEqual(set(new_target.targetged_items.all()), {self.inc1, self.inc2})

    def test_merged_targets_are_deleted(self):
        with self.assertRaises(Target.DoesNotExist):
            Target.objects.get(id=self.target1.id)
        with self.assertRaises(Target.DoesNotExist):
            Target.objects.get(id=self.target2.id)

class NationalityMergeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nation1 = Nationality.objects.create(title='Canada')
        cls.nation2 = Nationality.objects.create(title='Iran')
        cls.inc1 = IncidentPageFactory(target_nationality=cls.nation1.id)
        cls.inc2 = IncidentPageFactory(target_nationality=cls.nation2.id)
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

    def test_nations_only_have_one_m2m(self):
        """If Nationalitys have more than one related_object, data will be lost on merge"""
        self.assertEqual(len(Nationality._meta.related_objects), 1)

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
