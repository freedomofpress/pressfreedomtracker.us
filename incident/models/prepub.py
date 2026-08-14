import json
from collections import Counter
from datetime import date
from operator import itemgetter

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import (
    Count,
    F,
    Q,
)
from django.db.models.functions import Cast, TruncMonth

from wagtail.models import Orderable

from psycopg.types.range import Range

from common.models import CategoryPage
from geonames.models import GeoName
from incident.utils.db import MakeDateRange


class PrepublicationIncidentQuerySet(models.QuerySet):
    def all_exact_dates_after(self, lower_bound: date):
        """Returns a list of exact dates on which prepublication
        incidents took place, after or on a given lower bound date."""
        return self.filter(
            date__gte=lower_bound,
            date_precision=PrepublicationIncident.DatePrecision.DAY,
        ).values_list("date", flat=True)

    def aggregate_with_category_counts(self, lower_date_bound=None):
        results = PrepublicationIncident.objects.values(
            "date",
            city=F("location__name"),
            state=F("location__regcode"),
        )
        if lower_date_bound:
            results = results.filter(
                date__gte=lower_date_bound,
                date_precision=PrepublicationIncident.DatePrecision.DAY,
            )

        results = results.annotate(
            categories=ArrayAgg("categorizations__category__title"),
            incident_count=Count("pk", distinct=True),
        ).order_by("-date")

        max_count = 1
        for result in results:
            count = Counter(result["categories"])
            result["category_counts"] = json.dumps(
                sorted(
                    [{"category": k, "count": v} for k, v in count.items()],
                    key=itemgetter("category"),
                )
            )
            if (new_max_count := count.most_common(1)[0][1]) > max_count:
                max_count = new_max_count
        return results, max_count

    def fuzzy_date_filter(self, lower: date | None = None, upper: date | None = None):
        """Filter prepublication incidents by date range, accounting
        for date precision.

        Reproduces the logic of `IncidentPage.fuzzy_date_filter`.

        Keyword arguments:
        lower -- the lower bound of the date (which is included in the range). If `None`, then the range is unbounded below.
        upper -- the lower bound of the date (which is included in the range). If `None`, then the range is unbounded below.

        """
        target_range = Range(
            lower=lower,
            upper=upper,
            bounds="[]",
        )
        exact_date_match = Q(
            date__contained_by=target_range,
            date_precision=PrepublicationIncident.DatePrecision.DAY,
        )
        inexact_date_match = Q(
            date_precision=PrepublicationIncident.DatePrecision.MONTH,
            enclosing_month__overlap=target_range,
        )
        return self.annotate(
            enclosing_month=MakeDateRange(
                Cast(TruncMonth("date"), models.DateField()),
                Cast(
                    TruncMonth("date")
                    + Cast(models.Value("1 month"), models.DurationField()),
                    models.DateField(),
                ),
            )
        ).filter(exact_date_match | inexact_date_match)


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
    successful_rows = models.IntegerField(null=True, blank=True, default=None)
    completed_at = models.DateTimeField(auto_now=True)
    error_message = models.TextField(default="")

    class Meta:
        ordering = ["-completed_at"]

    def __str__(self):
        completed_at = self.completed_at.astimezone().replace(microsecond=0).isoformat()
        return f"completed_at={completed_at}, successful_rows={self.successful_rows}"


class PrepublicationSyncSkippedRow(models.Model):
    sync = models.ForeignKey(
        PrepublicationIncidentSync,
        on_delete=models.CASCADE,
        related_name="skipped_rows",
    )
    number = models.IntegerField()
    reason = models.TextField()

    def __str__(self):
        return f"row number={self.number}, reason='{self.reason}'"
