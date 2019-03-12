from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import FieldPanel


class EmailSignup(models.Model):
    email_address = models.EmailField(blank=False, null=False, unique=True)
    signup_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email_address


@register_setting
class EmailSettings(BaseSetting):
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

    panels = [
        FieldPanel('signup_prompt'),
        FieldPanel('success_text'),
    ]

    class Meta:
        verbose_name = 'Email Signups'
