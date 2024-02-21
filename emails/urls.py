from django.urls import re_path

from emails.views import email_signup_create


urlpatterns = [
    re_path(r'^create/$', email_signup_create, name='email-signup-create'),
]
