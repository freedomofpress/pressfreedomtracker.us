import csv
import datetime
import json
from collections import Counter
from io import StringIO

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import (
    Count,
    F,
)
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import View
from django.views.generic.edit import FormView

from wagtail.admin import messages

from incident.forms import LegalOrderImportForm
from incident.models import (
    IncidentPage,
    LegalOrder,
    LegalOrderUpdate,
    PrepublicationIncident,
    PrepublicationIncidentSync,
    PrepublicationSettings,
)
from incident.utils.csv import parse_row


class LegalOrderImportSpec:
    pass


class LegalOrderImportView(FormView):
    form_class = LegalOrderImportForm
    template_name = "modeladmin/legal_order_import_form.html"
    success_url = reverse_lazy("import_legal_orders:confirm")

    def form_valid(self, form):
        csv_file = form.cleaned_data["csv_file"]
        reader = csv.DictReader(StringIO(csv_file.read().decode("utf-8")))

        data = {}
        found_errors = False
        for n, row in enumerate(reader):
            source_row_number = n + 2
            result = parse_row(row)
            if not result.success:
                found_errors = True
                for error in result.errors:
                    message = f"Row {source_row_number}"
                    if error.column_name:
                        message += f", column {error.column_name}"
                    form.add_error("csv_file", f"{message}: {error.message}")
            else:
                data.update(result.value)
        if found_errors:
            return self.form_invalid(form)
        else:
            self.request.session["legal_order_import"] = data
            return super().form_valid(form)


class LegalOrderImportConfirmView(View):
    template_name = "modeladmin/legal_order_import_confirm.html"

    def get(self, request, *args, **kwargs):
        import_data = request.session["legal_order_import"]

        max_legal_orders = 0

        confirmation_data = {}
        incidents = IncidentPage.objects.in_bulk(list(import_data.keys()))
        for pk, legal_order_data in import_data.items():
            legal_orders = legal_order_data.get("legal_orders", [])
            max_legal_orders = max(max_legal_orders, len(legal_orders))

            confirmation_data[incidents[int(pk)]] = legal_order_data

        return render(
            request,
            self.template_name,
            {
                "confirmation_data": confirmation_data,
                "max_legal_orders": range(max_legal_orders),
            },
        )

    def post(self, request, *args, **kwargs):
        import_data = request.session.pop("legal_order_import", {})
        incidents = IncidentPage.objects.in_bulk(list(import_data.keys()))
        count = len(incidents)
        for pk, legal_order_data in import_data.items():
            incident = incidents[int(pk)]
            incident.legal_order_venue = legal_order_data["venue"]
            incident.legal_order_target = legal_order_data["target"]
            for legal_order in legal_order_data["legal_orders"]:
                initial_status, *statuses = legal_order["statuses"]
                new_order = LegalOrder.objects.create(
                    incident_page=incident,
                    order_type=legal_order["type"],
                    information_requested=legal_order["information_requested"],
                    status=initial_status["status"],
                    date=initial_status["date"],
                )
                LegalOrderUpdate.objects.bulk_create(
                    [
                        LegalOrderUpdate(
                            legal_order=new_order,
                            date=status["date"],
                            status=status["status"],
                        )
                        for status in statuses
                    ]
                )

            incident.save()

        messages.success(
            request, f"Legal orders imported successfully.  Count affected: {count}"
        )
        return HttpResponseRedirect(reverse("import_legal_orders:show_form"))


def dates_between(lower, upper):
    """Generator that yields dates in increments of one day between
    the given dates, inclusive of both endpoints."""
    current = lower
    while current <= upper:
        yield current
        current += datetime.timedelta(days=1)


def prepub_list(request):
    try:
        sync = PrepublicationIncidentSync.objects.get()
    except PrepublicationIncidentSync.DoesNotExist:
        raise Http404
    if PrepublicationIncident.objects.count() < 1:
        raise Http404

    prepub_settings = PrepublicationSettings.load(request_or_site=request)

    if not prepub_settings.is_enabled:
        raise Http404

    lower_bound = datetime.date.today() - prepub_settings.get_timespan()
    bar_chart_lower_bound = datetime.date.today() - datetime.timedelta(days=29)

    confirmed_by_date = Counter(
        IncidentPage.objects.live()
        .filter(date__gte=bar_chart_lower_bound)
        .values_list("date", flat=True)
    )

    unconfirmed_by_date = Counter(
        PrepublicationIncident.objects.filter(date__gte=lower_bound).values_list(
            "date", flat=True
        )
    )

    bar_chart_dataset = []

    for d in dates_between(bar_chart_lower_bound, datetime.date.today()):
        unconfirmed_count = unconfirmed_by_date.get(d, 0)
        confirmed_count = confirmed_by_date.get(d, 0)
        bar_chart_dataset.append(
            {
                "date": f"{d:%m/%d}",
                "count": unconfirmed_count + confirmed_count,
                "unconfirmed": unconfirmed_count,
                "confirmed": confirmed_count,
            }
        )

    prepubs = (
        PrepublicationIncident.objects.values(
            "date",
            city=F("location__name"),
            state=F("location__regcode"),
        )
        .filter(date__gte=lower_bound)
        .annotate(
            categories=ArrayAgg("categorizations__category__title"),
            incident_count=Count("pk", distinct=True),
        )
        .order_by("-date")
    )

    sync = PrepublicationIncidentSync.objects.get()

    for p in prepubs:
        p["category_counts"] = json.dumps(
            [{"category": k, "count": v} for k, v in Counter(p["categories"]).items()]
        )

    return TemplateResponse(
        request,
        "incident/prepub_list.html",
        {
            "prepubs": PrepublicationIncident.objects.aggregate_with_category_counts(
                lower_date_bound=lower_bound
            ),
            "updated_time": sync.completed_at.strftime("%H:%M %p %Z"),
            "timespan_display": prepub_settings.get_timespan_display(),
            "bar_chart_dataset": json.dumps(bar_chart_dataset),
        },
    )
