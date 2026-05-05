from django.urls import path

from emails.views import email_signup_create


urlpatterns = [
    path("create/", email_signup_create, name="email-signup-create"),
]
