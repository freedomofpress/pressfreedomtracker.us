import csv
from io import StringIO

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import View
from django.views.generic.edit import FormView
from wagtail.admin import messages

from common.views import MergeView
from incident.forms import (
    ChargeMergeForm,
    GovernmentWorkerMergeForm,
    InstitutionMergeForm,
    JournalistMergeForm,
    LawEnforcementOrganizationForm,
    LegalOrderImportForm,
    NationalityMergeForm,
    PoliticianOrPublicMergeForm,
    VenueMergeForm,
)
from incident.models import (
    Charge,
    IncidentCharge,
    IncidentPage,
    Institution,
    Journalist,
    TargetedJournalist,
    LegalOrder,
    LegalOrderUpdate,
)
from incident.utils.csv import parse_row


class ChargeMergeView(FormView):
    form_class = ChargeMergeForm
    template_name = 'modeladmin/merge_form.html'
    model_admin = None

    def get_success_url(self):
        return self.model_admin.url_helper.index_url

    def form_valid(self, form):
        models_to_merge = form.cleaned_data['models_to_merge']
        new_title = form.cleaned_data['title_for_merged_models']
        charge, _ = Charge.objects.get_or_create(title=new_title)

        IncidentCharge.objects.filter(charge__in=models_to_merge).update(charge=charge)
        models_to_merge.delete()
        return super().form_valid(form)


class LawEnforcementOrganizationMergeView(MergeView):
    form_class = LawEnforcementOrganizationForm


class NationalityMergeView(MergeView):
    form_class = NationalityMergeForm


class VenueMergeView(MergeView):
    form_class = VenueMergeForm


class PoliticianOrPublicMergeView(MergeView):
    form_class = PoliticianOrPublicMergeForm


class JournalistMergeView(FormView):
    form_class = JournalistMergeForm
    template_name = 'modeladmin/merge_form.html'
    model_admin = None

    def get_success_url(self):
        return self.model_admin.url_helper.index_url

    def form_valid(self, form):
        models_to_merge = form.cleaned_data['models_to_merge']
        new_journalist_title = form.cleaned_data['title_for_merged_models']

        journalist, _ = Journalist.objects.get_or_create(title=new_journalist_title)
        TargetedJournalist.objects.filter(journalist__in=models_to_merge).update(journalist=journalist)

        models_to_merge.delete()
        return super().form_valid(form)


class InstitutionMergeView(FormView):
    form_class = InstitutionMergeForm
    template_name = 'modeladmin/merge_form.html'
    model_admin = None

    def get_success_url(self):
        return self.model_admin.url_helper.index_url

    def form_valid(self, form):
        models_to_merge = form.cleaned_data['models_to_merge']
        new_inst_title = form.cleaned_data['title_for_merged_models']

        new_institution, _ = Institution.objects.get_or_create(title=new_inst_title)

        TargetedJournalist.objects.filter(
            institution__in=models_to_merge
        ).update(institution=new_institution)

        for incident in IncidentPage.objects.filter(targeted_institutions__in=models_to_merge):
            incident.targeted_institutions.add(new_institution)
            incident.save()

        models_to_merge.delete()

        return super().form_valid(form)


class GovernmentWorkerMergeView(MergeView):
    form_class = GovernmentWorkerMergeForm


class LegalOrderImportSpec:
    pass


class LegalOrderImportView(FormView):
    form_class = LegalOrderImportForm
    template_name = 'modeladmin/legal_order_import_form.html'
    success_url = reverse_lazy('import_legal_orders:confirm')

    def form_valid(self, form):
        csv_file = form.cleaned_data['csv_file']
        reader = csv.DictReader(StringIO(csv_file.read().decode('utf-8')))

        data = {}
        found_errors = False
        for n, row in enumerate(reader):
            source_row_number = n + 2
            result = parse_row(row)
            if not result.success:
                found_errors = True
                for error in result.errors:
                    message = f'Row {source_row_number}'
                    if error.column_name:
                        message += f', column {error.column_name}'
                    form.add_error('csv_file', f'{message}: {error.message}')
            else:
                data.update(result.value)
        if found_errors:
            return self.form_invalid(form)
        else:
            self.request.session['legal_order_import'] = data
            return super().form_valid(form)


class LegalOrderImportConfirmView(View):
    template_name = 'modeladmin/legal_order_import_confirm.html'

    def get(self, request, *args, **kwargs):
        import_data = request.session['legal_order_import']

        max_legal_orders = 0

        confirmation_data = {}
        incidents = IncidentPage.objects.in_bulk(list(import_data.keys()))
        for pk, legal_order_data in import_data.items():
            legal_orders = legal_order_data.get('legal_orders', [])
            max_legal_orders = max(
                max_legal_orders,
                len(legal_orders)
            )

            confirmation_data[incidents[int(pk)]] = legal_order_data

        return render(
            request, self.template_name, {
                'confirmation_data': confirmation_data,
                'max_legal_orders': range(max_legal_orders),
            }
        )

    def post(self, request, *args, **kwargs):
        import_data = request.session.pop('legal_order_import', {})
        incidents = IncidentPage.objects.in_bulk(list(import_data.keys()))
        count = len(incidents)
        for pk, legal_order_data in import_data.items():
            incident = incidents[int(pk)]
            incident.legal_order_venue = legal_order_data['venue']
            incident.legal_order_target = legal_order_data['target']
            for legal_order in legal_order_data['legal_orders']:
                initial_status, *statuses = legal_order['statuses']
                new_order = LegalOrder.objects.create(
                    incident_page=incident,
                    order_type=legal_order['type'],
                    information_requested=legal_order['information_requested'],
                    status=initial_status['status'],
                    date=initial_status['date'],
                )
                LegalOrderUpdate.objects.bulk_create([
                    LegalOrderUpdate(
                        legal_order=new_order,
                        date=status['date'],
                        status=status['status'],
                    ) for status in statuses
                ])

            incident.save()

        messages.success(
            request,
            f'Legal orders imported successfully.  Count affected: {count}'
        )
        return HttpResponseRedirect(reverse('import_legal_orders:show_form'))
