from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.test import TestCase, RequestFactory
from django.urls import reverse
from wagtail.models import Site
from wagtail.test.utils import WagtailTestUtils
from wagtail.test.utils.form_data import (
    inline_formset,
    nested_form_data,
    rich_text,
)

from home.tests.factories import HomePageFactory
from forms.tests.factories import (
    FormPageFactory,
    FormPageWithReplyToFieldFactory,
    FormPageWithAppendSubjectFieldsFactory,
)


class FormPageTestCase(TestCase):
    @classmethod
    def setUpTestData(kls):
        home_page = HomePageFactory.build()
        site, created = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                'site_name': 'Test site',
                'hostname': 'testserver',
                'port': '1111',
            }
        )
        if not created:
            site.save()
        root_page = site.root_page
        root_page.add_child(instance=home_page)

        kls.form_page = FormPageFactory.build()
        home_page.add_child(instance=kls.form_page)

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

    def test_page_renders_successfully(self):
        response = self.client.get(self.form_page.get_url())
        self.assertEqual(response.status_code, 200)

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


class ReplyToFieldsValidatorFormTests(TestCase, WagtailTestUtils):
    def setUp(self):
        self.root_page = Site.objects.get(is_default_site=True).root_page
        self.home_page = HomePageFactory.build()
        self.root_page.add_child(instance=self.home_page)
        self.login()

    def test_does_not_allow_multiple_fields_with_the_same_label_across_groups(self):
        post_data = nested_form_data({
            'title': 'Test form page',
            'slug': 'test-form-page',
            'intro': rich_text('<p>Test intro</p>'),
            'form_intro': 'Test form',
            'thank_you_text': rich_text('<p>Thanks (test)!</p>'),
            'button_text': 'Test button',
            'outro_title': 'Test outro',
            'outro_text': rich_text('<p>Test outro body</p>'),
            'from_address': 'from@example.com',
            'to_address': 'to@example.com',
            'subject': 'Test subject',
            'field_groups': inline_formset([
                {
                    'title': 'Test group',
                    'description': 'Test description',
                    'template': 'default',
                    'form_fields': inline_formset([
                        {
                            'label': 'Test label',
                            'help_text': 'Test',
                            'required': 'True',
                            'field_type': 'email',
                        },
                        {
                            'label': 'Test label 1',
                            'help_text': 'Test',
                            'required': 'True',
                            'field_type': 'email',
                        },
                    ])
                },
                {
                    'title': 'Test group 2',
                    'description': 'Test description',
                    'template': 'default',
                    'form_fields': inline_formset([
                        {
                            'label': 'Test label',
                            'help_text': 'Test',
                            'required': 'True',
                            'field_type': 'email',
                        },
                        {
                            'label': 'Test label 4',
                            'help_text': 'Test',
                            'required': 'True',
                            'field_type': 'email',
                        },
                    ])
                }
            ])
        })
        response = self.client.post(
            reverse(
                "wagtailadmin_pages:add",
                args=('forms', 'formpage', self.home_page.pk)
            ),
            post_data
        )
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'The page could not be created')
        self.assertContains(response, 'There is another field with the label Test label')

    def test_does_not_allow_multiple_fields_with_the_same_label(self):
        post_data = nested_form_data({
            'title': 'Test form page',
            'slug': 'test-form-page',
            'intro': rich_text('<p>Test intro</p>'),
            'form_intro': 'Test form',
            'thank_you_text': rich_text('<p>Thanks (test)!</p>'),
            'button_text': 'Test button',
            'outro_title': 'Test outro',
            'outro_text': rich_text('<p>Test outro body</p>'),
            'from_address': 'from@example.com',
            'to_address': 'to@example.com',
            'subject': 'Test subject',
            'field_groups': inline_formset([
                {
                    'title': 'Test group',
                    'description': 'Test description',
                    'template': 'default',
                    'form_fields': inline_formset([
                        {
                            'label': 'Test label',
                            'help_text': 'Test',
                            'required': 'True',
                            'field_type': 'email',
                        },
                        {
                            'label': 'Test label',
                            'help_text': 'Test',
                            'required': 'True',
                            'field_type': 'email',
                        },
                    ])
                }
            ])
        })
        response = self.client.post(
            reverse(
                "wagtailadmin_pages:add",
                args=('forms', 'formpage', self.home_page.pk)
            ),
            post_data
        )
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'The page could not be created')
        self.assertContains(response, 'There is another field with the label Test label')

    def test_does_not_allow_multiple_reply_to_fields(self):
        post_data = nested_form_data({
            'title': 'Test form page',
            'slug': 'test-form-page',
            'intro': rich_text('<p>Test intro</p>'),
            'form_intro': 'Test form',
            'thank_you_text': rich_text('<p>Thanks (test)!</p>'),
            'button_text': 'Test button',
            'outro_title': 'Test outro',
            'outro_text': rich_text('<p>Test outro body</p>'),
            'from_address': 'from@example.com',
            'to_address': 'to@example.com',
            'subject': 'Test subject',
            'field_groups': inline_formset([
                {
                    'title': 'Test group',
                    'description': 'Test description',
                    'template': 'default',
                    'form_fields': inline_formset([
                        {
                            'label': 'Test label',
                            'help_text': 'Test',
                            'required': 'True',
                            'field_type': 'email',
                            'use_as_reply_to': 'True',
                        },
                        {
                            'label': 'Test label 2',
                            'help_text': 'Test',
                            'required': 'True',
                            'field_type': 'email',
                            'use_as_reply_to': 'True',
                        },
                    ])
                }
            ])
        })
        response = self.client.post(
            reverse(
                "wagtailadmin_pages:add",
                args=('forms', 'formpage', self.home_page.pk)
            ),
            post_data
        )
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'The page could not be created')
        self.assertContains(response, 'Only one field per form may have this')


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
