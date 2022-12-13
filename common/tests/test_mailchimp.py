from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings
from mailchimp_marketing.api_client import ApiClientError
from wagtail.models import Site

from emails.devdata import EmailSettingsFactory
from emails.models import MailchimpGroup, Subscription
from ..utils import subscribe_for_site, ApiKeyMissingError, ApiError, compute_email_hash


class MailchimpSubscribeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = Site.objects.get(is_default_site=True)
        cls.email_settings_page = EmailSettingsFactory(site=cls.site)

        MailchimpGroup.objects.create(
            page=cls.email_settings_page,
            audience_id='Audience_1',
            group_id='Group_1'
        )
        MailchimpGroup.objects.create(
            page=cls.email_settings_page,
            audience_id='Audience_1',
            group_id='Group_2'
        )

    @override_settings(MAILCHIMP_API_KEY='KEY1')
    @mock.patch('mailchimp_marketing.Client')
    def test_subscribe_for_site_calls_mailchimp_api(self, mock_mailchimp_client):
        subscriber_email = 'test@example.com'
        subscription = Subscription(email=subscriber_email, full_name=None)

        instance = mock_mailchimp_client.return_value
        instance.lists = mock.PropertyMock()

        subscribe_for_site(self.site, subscription)

        instance.set_config.assert_called_with({'api_key': 'KEY1'})
        instance.lists.set_list_member.assert_called_with(
            'Audience_1',
            compute_email_hash(subscriber_email),
            {
                'email_address': subscriber_email,
                'status_if_new': 'pending',
                'interests': {
                    'Group_1': True,
                    'Group_2': True,
                }
            }
        )

    @override_settings(MAILCHIMP_API_KEY='KEY1')
    @mock.patch('mailchimp_marketing.Client')
    def test_subscribe_for_site_calls_mailchimp_api_with_fullname(self, mock_mailchimp_client):
        subscriber_email = 'test@example.com'
        subscriber_name = 'Jane Lane'
        subscription = Subscription(
            email=subscriber_email,
            full_name=subscriber_name,
        )

        instance = mock_mailchimp_client.return_value
        instance.lists = mock.PropertyMock()

        subscribe_for_site(self.site, subscription)

        instance.set_config.assert_called_with({'api_key': 'KEY1'})
        instance.lists.set_list_member.assert_called_with(
            'Audience_1',
            compute_email_hash(subscriber_email),
            {
                'email_address': subscriber_email,
                'status_if_new': 'pending',
                'interests': {
                    'Group_1': True,
                    'Group_2': True,
                },
                'merge_fields': {
                    'FULLNAME': subscriber_name
                },
            }
        )

    @override_settings()
    @mock.patch('mailchimp_marketing.Client')
    def test_subscribe_for_site_raises_error_if_no_api_key(self, mock_mailchimp_client):
        del settings.MAILCHIMP_API_KEY
        subscriber_email = 'test@example.com'

        instance = mock_mailchimp_client.return_value
        instance.lists = mock.PropertyMock()

        with self.assertRaises(ApiKeyMissingError):
            subscribe_for_site(self.site, subscriber_email)
        instance.set_config.assert_not_called()
        instance.lists.set_list_member.assert_not_called()

    @override_settings(MAILCHIMP_API_KEY='KEY1')
    @mock.patch('mailchimp_marketing.Client')
    def test_subscribe_for_site_raises_error_if_mailchimp_api_fails(self, mock_mailchimp_client):
        subscriber_email = 'test@example.com'
        subscription = Subscription(email=subscriber_email, full_name=None)

        instance = mock_mailchimp_client.return_value
        instance.lists = mock.PropertyMock()
        instance.lists.set_list_member.side_effect = ApiClientError(
            text='Cannot reverse the polarity',
        )

        with self.assertRaises(ApiError):
            subscribe_for_site(self.site, subscription)
