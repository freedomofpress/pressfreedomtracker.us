from wagtail_newsletter.campaign_backends.mailchimp import MailchimpCampaignBackend


class DisableTrackingBackend(MailchimpCampaignBackend):
    def get_campaign_request_body(self, **kwargs):
        body = super().get_campaign_request_body(**kwargs)
        # Add tracking settings to disable all tracking
        body["tracking"] = {
            "opens": False,
            "html_clicks": False,
            "text_clicks": False,
        }
        return body
