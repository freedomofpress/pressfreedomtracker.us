import csv
from io import StringIO

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.paginator import Paginator
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.decorators.vary import vary_on_headers
from django.views.generic import View
from django.views.generic.edit import FormView
from wagtail.admin.auth import (
    user_has_any_page_permission,
    user_passes_test,
)
from wagtail.admin.forms.search import SearchForm

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
)
from incident.utils.csv import parse_row


@vary_on_headers('X-Requested-With')
@user_passes_test(user_has_any_page_permission)
def incident_admin_search_view(request):
    pages = []
    q = None

    if 'q' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            q = form.cleaned_data['q']

            query = SearchQuery(q)
            vector = SearchVector('title', 'body')
            pages = IncidentPage.objects.annotate(search=vector).filter(search=query)
            paginator = Paginator(pages, per_page=25)
            pages = paginator.get_page(request.GET.get('p'))
    else:
        form = SearchForm()

    if request.is_ajax():
        return render(request, "wagtailadmin/incidentpages/search_results.html", {
            'pages': pages,
            'query_string': q,
            'pagination_query_params': ('q=%s' % q) if q else ''
        })
    else:
        return render(request, "wagtailadmin/incidentpages/search.html", {
            'search_form': form,
            'pages': pages,
            'query_string': q,
            'pagination_query_params': ('q=%s' % q) if q else ''
        })


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
