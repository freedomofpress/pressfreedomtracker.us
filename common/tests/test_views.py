import json
from unittest import mock

from django.core.files.base import ContentFile
from django.urls import reverse
from django.test import TestCase, override_settings
from wagtail.documents.models import Document
from common.models import CommonTag
from common.wagtail_hooks import CommonTagAdmin
from django.contrib.auth import get_user_model
from incident.tests.factories import (
    IncidentIndexPageFactory,
    IncidentPageFactory,
    TopicPageFactory,
)
from wagtail.core.models import Site
from mailchimp_marketing.api_client import ApiClientError

from emails.devdata import EmailSettingsFactory
from emails.models import Subscription
from common.utils import ApiError

User = get_user_model()


class DocumentDownloadTest(TestCase):
    def test_serve_inline(self):

        document = Document(title='Test')
        document.file.save(
            'test_serve_inline.txt',
            ContentFile('A test content.'),
        )

        response = self.client.get(
            reverse(
                'wagtaildocs_serve',
                args=(document.pk, document.filename),
            )
        )

        self.assertEqual(response['content-disposition'], 'inline; filename="{}"'.format(document.filename))


class MergeTagTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tag1 = CommonTag.objects.create(title='Rachel')
        cls.tag2 = CommonTag.objects.create(title='tags')
        cls.inc1 = IncidentPageFactory(tags=[cls.tag1])
        cls.inc2 = IncidentPageFactory(tags=[cls.tag2])
        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.new_tag_title = 'SomeTitle'
        self.response = self.client.post(
            CommonTagAdmin().url_helper.merge_url,
            {
                'models_to_merge': json.dumps([{
                    'label': self.tag1.title,
                    'pk': self.tag1.pk
                }, {
                    'label': self.tag2.title,
                    'pk': self.tag2.pk
                }]),
                'title_for_merged_models': self.new_tag_title
            }
        )


class MergeViewTest(MergeTagTestCase):
    def test_successful_request_redirects(self):
        self.assertEqual(self.response.status_code, 302)

    def test_correct_redirect_url(self):
        """Should redirect to the modelAdmin's index page"""
        self.assertEqual(self.response['location'], CommonTagAdmin().url_helper.index_url)

    def test_new_tag_created(self):
        CommonTag.objects.get(title=self.new_tag_title)

    def test_new_tag_has_old_tag_relationships(self):
        new_tag = CommonTag.objects.get(title=self.new_tag_title)
        self.assertEqual(set(new_tag.tagged_items.all()), {self.inc1, self.inc2})

    def test_merged_tags_are_deleted(self):
        with self.assertRaises(CommonTag.DoesNotExist):
            CommonTag.objects.get(pk=self.tag1.pk)
        with self.assertRaises(CommonTag.DoesNotExist):
            CommonTag.objects.get(pk=self.tag2.pk)


class MergeTagWithTopicPageTest(MergeTagTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.index = IncidentIndexPageFactory.create()
        cls.topic_page1 = TopicPageFactory(
            incident_tag=cls.tag1,
            incident_index_page=cls.index
        )
        cls.topic_page2 = TopicPageFactory(
            incident_tag=cls.tag2,
            incident_index_page=cls.index
        )

    def test_topic_page_incident_tag_should_become_new_tag(self):
        new_tag = CommonTag.objects.get(title=self.new_tag_title)
        self.topic_page1.refresh_from_db()
        self.topic_page2.refresh_from_db()

        self.assertEqual(self.topic_page1.incident_tag, new_tag)
        self.assertEqual(self.topic_page2.incident_tag, new_tag)


class MergeViewSameNameTest(TestCase):
    """
    If one of the merged tags has the same name as the post-merge version,
    the post-merge version should not be deleted.
    """
    @classmethod
    def setUpTestData(cls):
        cls.tag1 = CommonTag.objects.create(title='Rachel')
        cls.tag2 = CommonTag.objects.create(title='tags')
        cls.inc1 = IncidentPageFactory(tags=[cls.tag1])
        cls.inc2 = IncidentPageFactory(tags=[cls.tag2])
        cls.user = User.objects.create_superuser(username='test', password='test', email='test@test.com')

    def setUp(self):
        self.client.force_login(self.user)
        self.new_tag_title = self.tag1.title
        self.response = self.client.post(
            CommonTagAdmin().url_helper.merge_url,
            {
                'models_to_merge': json.dumps([{
                    'label': self.tag1.title,
                    'pk': self.tag1.pk
                }, {
                    'label': self.tag2.title,
                    'pk': self.tag2.pk
                }]),
                'title_for_merged_models': self.new_tag_title
            }
        )

    def test_successful_request_redirects(self):
        self.assertEqual(self.response.status_code, 302)

    def test_correct_redirect_url(self):
        """Should redirect to the modelAdmin's index page"""
        self.assertEqual(self.response['location'], CommonTagAdmin().url_helper.index_url)

    def test_merged_tag_exists(self):
        CommonTag.objects.get(title=self.new_tag_title)

    def test_new_tag_has_old_tag_relationships(self):
        new_tag = CommonTag.objects.get(title=self.new_tag_title)
        self.assertEqual(set(new_tag.tagged_items.all()), {self.inc1, self.inc2})

    def test_merged_tags_are_deleted(self):
        # tag1 shouldn't be deleted because it's being merged into.
        CommonTag.objects.get(pk=self.tag1.pk)
        with self.assertRaises(CommonTag.DoesNotExist):
            CommonTag.objects.get(pk=self.tag2.pk)


class AdminVersionTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_superuser(username='test', password='test', email='test@test.com')
        self.client.force_login(user)

    def test_full_version_url_returns_200_status(self):
        self.response = self.client.get('/admin/version/')
        self.assertEqual(self.response.status_code, 200)

    @mock.patch('common.views.open')
    def test_full_version_url_returns_200_status_filenotfound(self, mock_open):
        mock_open.side_effect = FileNotFoundError
        self.response = self.client.get('/admin/version/')
        self.assertEqual(self.response.status_code, 200)


class CsrfTokenViewTest(TestCase):
    def test_health_check_url_returns_200_status(self):
        self.response = self.client.get(reverse('csrf_token'))
        self.assertEqual(self.response.status_code, 200)


class MailchimpInterestViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testadmin', is_superuser=True)

    def setUp(self):
        fake_mc_data = mock.Mock()
        fake_mc_data.get_all_lists.return_value = {
            'lists': [{'id': '1', 'name': 'Test List'}]
        }
        fake_mc_data.get_list_interest_categories.return_value = {
            'categories': [{'id': '2', 'title': 'Test Category'}]
        }
        fake_mc_data.list_interest_category_interests.return_value = {
            'interests': [{'id': '3', 'name': 'Test Group'}]
        }

        self.mailchimp_lists = fake_mc_data

    def test_view_forbidden_if_not_logged_in(self):
        response = self.client.get(reverse('mailchimp_interests'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('wagtailadmin_login'), response.url)

    def test_view_reports_error_if_no_api_key(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('mailchimp_interests'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context_data['error'],
            'Mailchimp API key not found',
        )

    @override_settings(MAILCHIMP_API_KEY='KEY1')
    @mock.patch('mailchimp_marketing.Client')
    def test_view_reports_error_if_request_fails(self, mock_mailchimp_client):
        instance = mock_mailchimp_client.return_value
        instance.lists = mock.PropertyMock()
        instance.lists.get_all_lists.side_effect = ApiClientError(
            text='Cannot reverse the polarity'
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('mailchimp_interests'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context_data['error'],
            'Error connecting to Mailchimp: Cannot reverse the polarity',
        )

    @override_settings(MAILCHIMP_API_KEY='KEY1')
    @mock.patch('mailchimp_marketing.Client')
    def test_view_succeeds_if_logged_in(self, mock_mailchimp_client):
        instance = mock_mailchimp_client.return_value
        instance.lists = self.mailchimp_lists

        self.client.force_login(self.user)
        response = self.client.get(reverse('mailchimp_interests'))
        self.assertEqual(response.status_code, 200)

    @override_settings(MAILCHIMP_API_KEY='KEY1')
    @mock.patch('mailchimp_marketing.Client')
    def test_view_includes_interest_and_audience_ids(self, mock_mailchimp_client):
        instance = mock_mailchimp_client.return_value
        instance.lists = self.mailchimp_lists

        self.client.force_login(self.user)
        response = self.client.get(reverse('mailchimp_interests'))
        self.assertEqual(
            response.context_data['table_data'],
            [
                ('Test List', '1', 'Test Category', 'Test Group', '3')
            ]
        )


class SubscribeForSiteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.email_settings_page = EmailSettingsFactory(site=cls.site)

    def test_ajax_subscribe_view_for_invalid_json_yields_400(self):
        self.response = self.client.post(
            reverse('subscribe_for_site'),
            HTTP_ACCEPT='application/json',
            content_type='application/json',
            data='invalid-json',
        )
        self.assertEqual(self.response.status_code, 400)

    def test_ajax_subscribe_view_with_missing_email_yields_400(self):
        self.response = self.client.post(
            reverse('subscribe_for_site'),
            HTTP_ACCEPT='application/json',
            content_type='application/json',
            data=json.dumps({'vegetable': 'radish'}),
        )
        self.assertEqual(self.response.status_code, 400)

    @mock.patch('common.views.subscribe_for_site')
    def test_subscribe_view_ajax_succeeds(self, mock_subscribe):
        email = 'test3@example.com'
        self.response = self.client.post(
            reverse('subscribe_for_site'),
            HTTP_ACCEPT='application/json',
            content_type='application/json',
            data=json.dumps({'email': email}),
        )
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(
            self.response.json(), {'success': True}
        )
        mock_subscribe.assert_called_once_with(
            self.site,
            Subscription(email=email, full_name=None)
        )

    @mock.patch('common.views.subscribe_for_site')
    def test_subscribe_view_handles_subscription_errors(self, mock_subscribe):
        mock_subscribe.side_effect = ApiError(text='error', status_code=404)
        response = self.client.post(
            reverse('subscribe_for_site'),
            HTTP_ACCEPT='application/json',
            content_type='application/json',
            data=json.dumps({'email': 'test4@example.com'}),
            HTTP_CF_CONNECTING_IP='8.8.8.8',
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])

    @mock.patch('common.views.subscribe_for_site')
    def test_subscribe_view_nonajax_handles_subscription_errors(self, mock_subscribe):
        mock_subscribe.side_effect = ApiError(text='error', status_code=404)
        response = self.client.post(
            reverse('subscribe_for_site'),
            {'email': 'test4@example.com'},
            HTTP_ACCEPT='text/html',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'An internal error occurred',
            response.content.decode('utf-8'),
        )

    @mock.patch('common.views.subscribe_for_site')
    def test_subscribe_view_nonajax_succeeds(self, mock_subscribe):
        email = 'test3@example.com'
        self.response = self.client.post(
            reverse('subscribe_for_site'),
            {'email': email},
            HTTP_ACCEPT='text/html',
        )
        self.assertEqual(self.response.status_code, 200)
        # self.assertEqual(self.response.url, reverse('subscribe_thanks'))
        mock_subscribe.assert_called_once_with(
            self.site,
            Subscription(email=email, full_name=None)
        )

    def test_nonajax_subscribe_view_with_missing_email_yields_error_message(self):
        response = self.client.post(
            reverse('subscribe_for_site'),
            {'vegetable': 'radish'},
            HTTP_ACCEPT='text/html',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'Invalid data submitted',
            response.content.decode('utf-8'),
        )


class HealthCheckTestCase(TestCase):
    def test_health_check_url_returns_200_status(self):
        self.response = self.client.get('/health/ok/')
        self.assertEqual(self.response.status_code, 200)

    def test_version_info_url_returns_200_status(self):
        self.response = self.client.get('/health/version/')
        self.assertEqual(self.response.status_code, 200)

    @mock.patch('common.views.open')
    def test_version_info_url_returns_200_status_filenotfound(self, mock_open):
        mock_open.side_effect = FileNotFoundError
        self.response = self.client.get('/health/version/')
        self.assertEqual(self.response.status_code, 200)
