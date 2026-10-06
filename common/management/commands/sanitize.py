"""Sanitize production database for pressfreedomtracker.us environments.

Usage:
    python manage.py sanitize -r hostname=staging.pressfreedomtracker.us

    # Skip interactive confirmation prompt
    python manage.py sanitize -r hostname=staging.pressfreedomtracker.us --confirm

    # Preserve CMS users:
    python manage.py sanitize -r hostname=staging.pressfreedomtracker.us --confirm --no-mangle auth.User

    # Preserve Django session data:
    python manage.py sanitize -r hostname=dev.pressfreedomtracker.us --confirm --no-truncate sessions.Session

    # Keep form submissions:
    python manage.py sanitize -r hostname=dev.pressfreedomtracker.us --confirm --no-truncate wagtailforms.FormSubmission

    # Keep newsletter signups:
    python manage.py sanitize -r hostname=dev.pressfreedomtracker.us --confirm --no-truncate emails.EmailSignup
"""

from fpfwagtailcommon.utils.management.commands.sanitize_base import (
    SanitizationProfile,
    SanitizeBaseCommand,
)


class Command(SanitizeBaseCommand):
    help = "Sanitize a pressfreedomtracker.us database"

    profile = SanitizationProfile(
        mangle_tables={
            "auth.User": {
                "password": "[REDACTED]",
                "email": "no-reply@invalid.freedom.press",
            },
            "wagtailcore.Site": {
                "hostname": "{hostname}",
            },
        },
        truncate_tables=[
            "sessions.Session",
            "emails.EmailSignup",
            "wagtailforms.FormSubmission",
        ],
    )
