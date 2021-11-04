from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    InlinePanel,
)


class EmailSignup(models.Model):
    email_address = models.EmailField(blank=False, null=False, unique=True)
    signup_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email_address


@register_setting
class EmailSettings(BaseSetting, ClusterableModel):
    signup_prompt = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        default='Sign up to receive emails from Press Freedom Tracker',
    )
    success_text = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        default='Thanks for signing up!',
    )
    mailchimp_collect_name = models.BooleanField(
        verbose_name='Enable name field',
        help_text='If checked, collect full name information in Mailchimp form',
        default=False,
    )

    panels = [
        FieldPanel('signup_prompt'),
        FieldPanel('success_text'),
        MultiFieldPanel(
            [
                InlinePanel(
                    'mailchimp_groups',
                    label='Group for signups',
                    max_num=1,
                ),
                FieldPanel('mailchimp_collect_name'),
            ],
            heading='Mailchimp',
            classname='collapsible',
        ),
    ]

    class Meta:
        verbose_name = 'Email Signups'


class MailchimpGroup(models.Model):
    page = ParentalKey(
        EmailSettings,
        related_name='mailchimp_groups',
        on_delete=models.CASCADE,
    )
    category_id = models.IntegerField(
        help_text='First number in the "name" field from the signup form input line.',
    )
    group_id = models.IntegerField(
        help_text='Second number in the "name" field from the signup form input line.',
    )
