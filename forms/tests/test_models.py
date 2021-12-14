import unittest

from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.test import TestCase, RequestFactory
from wagtail.core.models import Site, Page

from home.tests.factories import HomePageFactory
from forms.tests.factories import (
    FormPageFactory,
    FormPageWithReplyToFieldFactory,
    FormPageWithAppendSubjectFieldsFactory,
)


class FormPageTestCase(TestCase):
    @classmethod
    def setUpTestData(kls):
        Page.objects.filter(slug='home').delete()
        root_page = Page.objects.get(title='Root')
        home_page = HomePageFactory.build()
        root_page.add_child(instance=home_page)
        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'site_name': 'Test site',
                'hostname': 'testserver',
                'port': '1111',
                'root_page': home_page,
            }
        )
        if not created:
            site.root_page = home_page
            site.save()

        kls.form_page = FormPageFactory.build()
        home_page.add_child(instance=kls.form_page)

    @unittest.skip("Skipping till templates have been added")
    def test_cache_control_header_private(self):
        response = self.client.get(self.form_page.get_full_url())
        self.assertEqual(response['cache-control'], 'private')


class ReplyToFieldsTestCase(TestCase):
    @classmethod
    def setUpTestData(kls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        home_page = HomePageFactory.build()
        root_page.add_child(instance=home_page)

        # site = Site.objects.get(is_default_site=True)
        # root_page = site.root_page
        kls.form_page = FormPageWithReplyToFieldFactory(
            parent=home_page,
            title='Form',
            from_address='sender@example.com',
            to_address='receiver@example.com',
            slug='form',
        )
        # root_page.add_child(instance=kls.form_page)

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

    def test_reply_to_header_absent_if_value_absent(self):
        factory = RequestFactory()
        request = factory.post(self.form_page.get_url(), {})
        form = self.form_page.get_form(
            request.POST,
            request.FILES,
            page=self,
            user=AnonymousUser(),
        )

        self.form_page.send_mail(form)


class AppendSubjectFieldsTestCase(TestCase):
    @classmethod
    def setUpTestData(kls):
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
        home_page = HomePageFactory.build()
        root_page.add_child(instance=home_page)
        kls.form_page = FormPageWithAppendSubjectFieldsFactory(
            parent=home_page,
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
            f'{self.form_page.subject} - {topic} - {theme}'
        )
