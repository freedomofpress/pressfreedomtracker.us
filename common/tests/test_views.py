from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from wagtail.wagtaildocs.models import Document
from common.models import CommonTag
from common.wagtail_hooks import CommonTagAdmin
from django.contrib.auth import get_user_model
from incident.tests.factories import IncidentPageFactory
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
                args=(document.id, document.filename),
            )
        )

        self.assertEqual(response['content-disposition'], 'inline; filename="{}"'.format(document.filename))


class MergeViewTest(TestCase):
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
                    'id': self.tag1.id
                }, {
                    'label': self.tag2.title,
                    'id': self.tag2.id
                }]),
                'title_for_merged_models': self.new_tag_title
            }
        )

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
            CommonTag.objects.get(id=self.tag1.id)
        with self.assertRaises(CommonTag.DoesNotExist):
            CommonTag.objects.get(id=self.tag2.id)
