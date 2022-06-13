from collections import defaultdict

import mailchimp_marketing
from django.conf import settings


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


def subscribe_for_site(subscription):
    """Create subscriptions for the Mailchimp groups belonging to the site.
    """
    if not getattr(settings, 'MAILCHIMP_API_KEY', None):
        raise ApiKeyMissingError

    try:
        client = mailchimp_marketing.Client()
        client.set_config(
            {'api_key': settings.MAILCHIMP_API_KEY}
        )
        groups_by_audience = defaultdict(list)
        for group in page.mailchimp_groups.all():
            groups_by_audience[group.audience_id].append(group.group_id)

        for audience_id, group_ids in groups_by_audience.items():
            member_info = {
                'email_address': subscription.email,
                'status': 'pending',
                'interests': {
                    group_id: True for group_id in group_ids
                }
            }
            if subscription.full_name:
                member_info['merge_fields'] = {
                    'FULLNAME': subscription.full_name
                }

            client.lists.add_list_member(audience_id, member_info)
    except mailchimp_marketing.api_client.ApiClientError as err:
        raise ApiError(err.text, err.status_code)
