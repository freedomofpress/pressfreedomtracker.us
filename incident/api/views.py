from typing import TYPE_CHECKING

from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.pagination import CursorPagination
from rest_framework_csv.renderers import PaginatedCSVRenderer

from incident.api.serializers import IncidentSerializer, FlatIncidentSerializer
from incident.utils.incident_filter import IncidentFilter

if TYPE_CHECKING:
    from django.http import HttpResponse


class IncidentCursorPagination(CursorPagination):
    page_size = None
    page_size_query_param = 'limit'
    ordering = '-unique_date'


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IncidentSerializer
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (PaginatedCSVRenderer,)
    pagination_class = IncidentCursorPagination

    def dispatch(self, *args, **kwargs) -> 'HttpResponse':
        response = super().dispatch(*args, **kwargs)

        # Allow requests from any orign to allow this to be an accessible API
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET,OPTIONS,HEAD'

        return response

    def get_renderer_context(self):
        context = super().get_renderer_context()

        # Get set of fields from serializer that has been pruned
        # according to request's query-string parameters.
        context['header'] = list(self.get_serializer().fields.keys())
        return context

    def get_serializer_class(self):
        if self.request.accepted_renderer.format == 'csv':
            return FlatIncidentSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        incident_filter = IncidentFilter(self.request.GET)
        incidents = incident_filter.get_queryset()

        return incidents.with_most_recent_update().with_public_associations()
