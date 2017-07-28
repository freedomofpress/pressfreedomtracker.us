from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register

from emails.models import EmailSignup


@modeladmin_register
class EmailSignupModelAdmin(ModelAdmin):
    model = EmailSignup
    list_display = (
        'id',
        'email_address',
        'signup_time',
    )
