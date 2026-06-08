import csv
import datetime
from collections import Counter
from io import StringIO

from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import (
    Count,
    F,
)
from django.http import HttpResponseRedirect
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


def prepub_list(request):
    prepub_settings = PrepublicationSettings.load(request_or_site=request)
    lower_bound = datetime.date.today() - prepub_settings.get_timespan()

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
        p["category_counts"] = Counter(p["categories"])

    return TemplateResponse(
        request,
        "incident/prepub_list.html",
        {
            "prepubs": prepubs,
            "updated_time": sync.completed_at.strftime("%H:%M %p %Z"),
            "timespan_display": prepub_settings.get_timespan_display(),
        },
    )
