from django.contrib.auth.models import Permission
from wagtail import hooks


@hooks.register("register_permissions")
def register_permissions():
    return Permission.objects.filter(
        content_type__app_label="blog",
        codename__in=[
            "add_customrecipients",
            "change_customrecipients",
            "delete_customrecipients",
            "save_campaign_blogpage",
            "send_test_email_blogpage",
            "send_campaign_blogpage",
            "schedule_campaign_blogpage",
            "unschedule_campaign_blogpage",
            "get_report_blogpage",
            "access_newsletter_tab_blogpage",
        ],
    )
