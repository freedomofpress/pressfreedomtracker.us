import json
from collections import Counter

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import (
    Count,
    F,
)

from wagtail.models import Orderable

from common.models import CategoryPage
from geonames.models import GeoName


class PrepublicationIncidentQuerySet(models.QuerySet):
    def aggregate_with_category_counts(self, lower_date_bound=None):
        results = PrepublicationIncident.objects.values(
            "date",
            city=F("location__name"),
            state=F("location__regcode"),
        )
        if lower_date_bound:
            results = results.filter(date__gte=lower_date_bound)

        results = results.annotate(
            categories=ArrayAgg("categorizations__category__title"),
            incident_count=Count("pk", distinct=True),
        ).order_by("-date")

        for result in results:
            result["category_counts"] = json.dumps(
                [
                    {"category": k, "count": v}
                    for k, v in Counter(result["categories"]).items()
                ]
            )
        return results


class PrepublicationIncident(models.Model):
    objects = PrepublicationIncidentQuerySet.as_manager()

    DatePrecision = models.IntegerChoices("DatePrecision", "DAY MONTH")

    date = models.DateField()
    date_precision = models.IntegerField(
        choices=DatePrecision, default=DatePrecision.DAY
    )
    location = models.ForeignKey(
        GeoName,
        on_delete=models.CASCADE,
        related_name="+",
    )

    def __str__(self):
        match self.date_precision:
            case self.DatePrecision.DAY:
                return self.date.isoformat()
            case self.DatePrecision.MONTH:
                return self.date.strftime("%Y-%m")
        return f"{self.date} ({self.date_precision})"


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
