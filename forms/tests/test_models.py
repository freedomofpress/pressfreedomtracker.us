from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.test import TestCase, RequestFactory
from wagtail.core.models import Site

from forms.tests.factories import (
    FormPageFactory,
    FormPageWithReplyToFieldFactory,
    FormPageWithAppendSubjectFieldsFactory,
)


class FormPageTest(TestCase):
    def test_cache_control_header_private(self):
        site = Site.objects.get()
        form_page = FormPageFactory(parent=site.root_page)

        response = self.client.get(form_page.get_url())

        self.assertEqual(response['cache-control'], 'private')


class ReplyToFields(TestCase):
    @classmethod
    def setUpTestData(kls):
        site = Site.objects.get()
        kls.form_page = FormPageWithReplyToFieldFactory(
            parent=site.root_page,
            title='Form',
            from_address='sender@example.com',
            to_address='receiver@example.com',
            slug='form',
        )

    def test_reply_to_header_form_fields(self):
        factory = RequestFactory()
        reply_to = 'hello@example.com'
        request = factory.post(self.form_page.get_url(), {'email_address': reply_to})
        form = self.form_page.get_form(
            request.POST,
            request.FILES,
            page=self,
            user=AnonymousUser(),
        )

        self.form_page.send_mail(form)
        self.assertEqual(mail.outbox[0].reply_to, [reply_to])

class AppendSubjectFields(TestCase):
    @classmethod
    def setUpTestData(kls):
        site = Site.objects.get()
        kls.form_page = FormPageWithAppendSubjectFieldsFactory(
            parent=site.root_page,
            title='Form',
            subject='Base Subject',
            from_address='sender@example.com',
            to_address='receiver@example.com',
            slug='form',
        )

    def test_subject_form_fields(self):
        factory = RequestFactory()
        theme = 'TPS Report Cover Sheets'
        topic = 'Compliance'
        request = factory.post(self.form_page.get_url(), {'topic': topic, 'theme': theme})
        form = self.form_page.get_form(
            request.POST,
            request.FILES,
            page=self,
            user=AnonymousUser(),
        )

        self.form_page.send_mail(form)
        self.assertEqual(
            mail.outbox[0].subject,
            '{0} - {1} - {2}'.format(self.form_page.subject, theme, topic)
        )
