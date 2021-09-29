from django.core.files.base import ContentFile
from django.urls import reverse
from django.test import TestCase
from wagtail.documents.models import Document
from wagtail.tests.utils import WagtailPageTests
from common.models import CommonTag
from common.wagtail_hooks import CommonTagAdmin
from django.contrib.auth import get_user_model
from incident.tests.factories import (
    IncidentIndexPageFactory,
    IncidentPageFactory,
    TopicPageFactory,
)
from unittest import mock
import json

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


class MergeTagFormTestCase(WagtailPageTests):
    def test_getting_the_form_succeeds(self):
        self.response = self.client.get(CommonTagAdmin().url_helper.merge_url)
        self.assertEqual(self.response.status_code, 200)


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
