from django.contrib.postgres.search import SearchQuery, SearchVector
from django.shortcuts import render
from django.views.decorators.vary import vary_on_headers
from wagtail.utils.pagination import paginate
from wagtail.wagtailadmin.forms import SearchForm
from wagtail.wagtailadmin.utils import (
    user_has_any_page_permission,
    user_passes_test,
)

from common.views import MergeView
from incident.forms import TargetMergeForm, ChargeMergeForm, VenueMergeForm, NationalityMergeForm, PoliticianOrPublicMergeForm
from incident.models.incident_page import IncidentPage


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
            paginator, pages = paginate(request, pages)
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


class TargetMergeView(MergeView):
    form_class = TargetMergeForm


class ChargeMergeView(MergeView):
    form_class = ChargeMergeForm


class NationalityMergeView(MergeView):
    form_class = NationalityMergeForm


class VenueMergeView(MergeView):
    form_class = VenueMergeForm


class PoliticianOrPublicMergeView(MergeView):
    form_class = PoliticianOrPublicMergeForm
