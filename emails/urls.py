from django.conf.urls import url

from emails.views import email_signup_create


urlpatterns = [
    url(r'^create/$', email_signup_create, name='email-signup-create'),
]
