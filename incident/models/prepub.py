from django.db import models

from wagtail.models import Orderable

from common.models import CategoryPage
from geonames.models import GeoName


class PrepublicationIncident(models.Model):
    date = models.DateField()
    location = models.ForeignKey(
        GeoName,
        on_delete=models.CASCADE,
        related_name="+",
    )


class PrepublicationIncidentCategory(Orderable):
    incident = models.ForeignKey(
        PrepublicationIncident,
        on_delete=models.CASCADE,
        related_name="categorizations",
    )
    category = models.ForeignKey(
        CategoryPage,
        on_delete=models.CASCADE,
        related_name="+",
    )


class PrepublicationIncidentSync(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "SUCCESS"
        INVALID_DATA = "INVALID_DATA"
        FAILED = "FAILED"

    status = models.CharField(max_length=255, choices=Status.choices)
    completed_at = models.DateTimeField(auto_now=True)
    message = models.TextField(default="")

    class Meta:
        ordering = ["-completed_at"]
