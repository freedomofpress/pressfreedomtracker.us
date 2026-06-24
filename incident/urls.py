from django.urls import path

from . import views


urlpatterns = [
    path("unconfirmed-incidents/", views.prepub_list, name="prepub_list"),
]
