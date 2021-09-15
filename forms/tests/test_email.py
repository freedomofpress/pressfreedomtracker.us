from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings

from forms.email import send_mail


class TestEmail(TestCase):
    def test_sends_email_messages(self):
        text_content = 'This is an important message.'
        send_mail('Subject', text_content, ['test@example.com'], 'from@example.com')

        self.assertEqual(mail.outbox[0].subject, 'Subject')
        self.assertEqual(mail.outbox[0].from_email, 'from@example.com')
        self.assertEqual(mail.outbox[0].alternatives, [])

    def test_sends_html_email_messages(self):
        text_content = 'This is an important message.'
        html_content = '<p>This is an <strong>important</strong> message.</p>'
        send_mail(
            'Subject',
            text_content,
            ['test@example.com'],
            'from@example.com',
            html_message=html_content,
        )
        self.assertEqual(mail.outbox[0].alternatives[0][1], 'text/html')

    @override_settings(WAGTAILADMIN_NOTIFICATION_FROM_EMAIL='admin@example.com')
    @override_settings(DEFAULT_FROM_EMAIL='default@example.com')
    def test_falls_back_on_notification_settings_for_from_address(self):
        text_content = 'This is an important message.'
        send_mail('Subject', text_content, ['test@example.com'], from_email=None)
        self.assertEqual(mail.outbox[0].from_email, 'admin@example.com')

    @override_settings(DEFAULT_FROM_EMAIL='default@example.com')
    def test_falls_back_on_default_settings_for_from_address(self):
        text_content = 'This is an important message.'
        send_mail('Subject', text_content, ['test@example.com'], from_email=None)
        self.assertEqual(mail.outbox[0].from_email, 'default@example.com')

    @override_settings()
    def test_falls_back_on_local_settings_for_from_address(self):
        del settings.DEFAULT_FROM_EMAIL
        text_content = 'This is an important message.'
        send_mail('Subject', text_content, ['test@example.com'], from_email=None)
        self.assertEqual(mail.outbox[0].from_email, 'webmaster@localhost')
