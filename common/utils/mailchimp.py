import hashlib
from collections import defaultdict

import mailchimp_marketing
from django.conf import settings
from emails.models import EmailSettings


class MailchimpError(Exception):
    """Base class for errors related to Mailchimp."""
    pass


class ApiKeyMissingError(MailchimpError):
    """Raised when the Mailchimp API key cannot be found."""
    pass


class ApiError(MailchimpError):
    """Raised when the Mailchimp API key cannot be found."""
    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code


def subscribe_for_site(site, subscription):
    """Create subscriptions for the Mailchimp groups belonging to the site.
    """
    if not getattr(settings, 'MAILCHIMP_API_KEY', None):
        raise ApiKeyMissingError('API Key Missing')

    try:
        client = mailchimp_marketing.Client()
        client.set_config(
            {'api_key': settings.MAILCHIMP_API_KEY}
        )
        groups_by_audience = defaultdict(list)
        email_settings = EmailSettings.for_site(site)
        for group in email_settings.mailchimp_groups.all():
            groups_by_audience[group.audience_id].append(group.group_id)

        for audience_id, group_ids in groups_by_audience.items():
            member_info = {
                'email_address': subscription.email,
                'status_if_new': 'pending',
                'interests': {
                    group_id: True for group_id in group_ids
                }
            }
            if subscription.full_name:
                member_info['merge_fields'] = {
                    'FULLNAME': subscription.full_name
                }

            client.lists.set_list_member(
                audience_id,
                compute_email_hash(subscription.email),
                member_info,
            )
    except mailchimp_marketing.api_client.ApiClientError as err:
        raise ApiError(err.text, err.status_code)


def compute_email_hash(email):
    """Compute the MD5 hash of the lowercase version of the list
    member's email address.  Required by Mailchimp.
    """
    return hashlib.md5(
        str(email).lower().encode(),
        usedforsecurity=False,
    ).hexdigest()
