from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test import TestCase
from wagtail.wagtaildocs.models import Document


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
