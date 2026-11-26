import copy
import json
from typing import TYPE_CHECKING

from django.db import models
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods

from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, path
from wagtail.models import Page, Site

from marshmallow import EXCLUDE, Schema, fields

from common.models import MetadataPageMixin
from common.models.settings import SearchSettings
from common.utils import DEFAULT_PAGE_KEY, paginate
from incident.feeds import IncidentIndexPageFeed
from incident.models.incident_page import IncidentPage
from incident.utils.forms import get_filter_forms
from incident.utils.incident_filter import (
    IncidentFilter,
    ManyRelationValue,
    get_serialized_filters,
)


if TYPE_CHECKING:
    from django.http import HttpRequest


class SummarySchema(Schema):
    class Meta:
        # This schema is populated from the incident filter results
        # summary, which can contain dynamic fields.  EXCLUDE tells
        # the schema to ignore those.
        unknown = EXCLUDE

    total = fields.Integer(data_key="Total Results")
    journalists = fields.Integer(data_key="Journalists affected")
    institutions = fields.Integer(data_key="Institutions affected")


class IncidentIndexPage(RoutablePageMixin, MetadataPageMixin, Page):
    feed_limit = models.PositiveIntegerField(
        default=1000,
        null=True,
        help_text="Maximum number of incidents to be included in the "
        "syndication feed. 0 for unlimited.",
    )
    feed_per_page = models.PositiveIntegerField(
        default=20,
        null=True,
        help_text="Maximum number of incidents to be included per page "
        "in the syndication feed.",
    )

    content_panels = Page.content_panels
    settings_panels = Page.settings_panels + [
        FieldPanel("feed_limit"),
        FieldPanel("feed_per_page"),
    ]

    subpage_types = ["incident.IncidentPage"]

    @path("export/")
    @method_decorator(require_http_methods(["HEAD", "GET", "OPTIONS"]))
    def export_view(self, request: HttpRequest) -> HttpResponse:
        # Imported here because the API views import incident.models.
        from incident.api.views import IncidentExportViewSet

        return IncidentExportViewSet.as_view({"get": "list"})(request)

    def handle_options_request(self, request, *args, **kwargs):
        """
        Override Wagtail's default OPTIONS handling to add CORS headers,
        required for cross-origin access to the export API endpoint.
        """
        response = super().handle_options_request(request, *args, **kwargs)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET,OPTIONS,HEAD"
        return response

    @path("summary/")
    @method_decorator(require_http_methods(["GET"]))
    def summary(self, request):
        incident_filter = IncidentFilter(request.GET)
        summary = incident_filter.get_summary()
        result = SummarySchema().load(dict(summary))
        return JsonResponse(result)

    @path("feed/")
    def feed(self, request):
        return IncidentIndexPageFeed(self)(request)

    def get_incidents(self):
        """Returns all published incident pages"""
        return (
            IncidentPage.objects.live()
            .with_most_recent_update()
            .annotate(
                # Incidents without any updates have a null latest_update, so
                # fall back to the incident date to keep them in the ordering.
                last_update_or_date=Coalesce(
                    "latest_update",
                    "date",
                ),
            )
            .order_by(
                "-last_update_or_date",
                "path",
            )
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Before perf change:
        # context['all_incident_count'] = len(IncidentFilter({}).get_queryset())

        # Quickest:
        context["all_incident_count"] = IncidentPage.objects.live().count()

        # Could also be:
        # context['all_incident_count'] = IncidentFilter({}).get_queryset().count()

        incident_filter = IncidentFilter(request.GET)
        context["serialized_filters"] = json.dumps(get_serialized_filters())

        search_settings = SearchSettings.for_site(Site.find_for_request(request))
        if search_settings.data_download_page:
            context["export_path"] = (
                search_settings.data_download_page.get_url()
            )  # pragma: no cover
        else:
            context["export_path"] = self.url + self.reverse_subpage("export_view")

        if search_settings.learn_more_page:
            context["learn_more_path"] = search_settings.learn_more_page.get_url()

        incident_filter.clean()
        context["search_value"] = incident_filter.cleaned_data.get("search", "")

        if incident_filter.cleaned_data:
            export_filter_data = copy.deepcopy(incident_filter.cleaned_data)
            for name, value in export_filter_data.items():
                if isinstance(value, ManyRelationValue):
                    filter_values = [str(i) for i in value.pks] + value.strings
                    export_filter_data[name] = ",".join(filter_values)

            context["filtered_export_path"] = (
                context["export_path"] + "?" + incident_filter.get_url_parameters()
            )

        incident_qs = (
            incident_filter.get_queryset()
            .with_public_associations()
            .with_most_recent_update()
        )
        paginator, entries = paginate(
            request, incident_qs, page_key=DEFAULT_PAGE_KEY, per_page=20, orphans=5
        )

        context["entries_page"] = entries
        context["paginator"] = paginator

        get_data = request.GET.copy()
        context["sort_choices"] = []
        for value, label in IncidentFilter.SortOptions.choices:
            get_data["sort"] = value
            context["sort_choices"].append(
                (get_data.urlencode(), label, value == incident_filter.sort.value)
            )
        context["selected_sort"] = incident_filter.sort

        # Before perf change:
        # context['incident_count'] = len(incident_qs)

        # Quickest:
        context["incident_count"] = paginator.count

        # Could also be:
        # context['incident_count'] = incident_qs.count()

        context["filters"] = get_filter_forms(
            request, json.loads(context["serialized_filters"])
        )

        return context

    def get_cache_tag(self):
        return f"incident-index-{self.pk}"

    def serve(self, request, *args, **kwargs):
        response = super().serve(request, *args, **kwargs)

        # We set a cache tag here so that elsewhere we can purge all subroutes
        # of the incident index page (including paginated and filtered URLs)
        # simultaneously
        response["Cache-Tag"] = self.get_cache_tag()
        return response
