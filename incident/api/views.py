from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.pagination import CursorPagination
from rest_framework_csv.renderers import PaginatedCSVRenderer

from incident.api.serializers import IncidentSerializer, FlatIncidentSerializer
from incident.utils.incident_filter import IncidentFilter


class IncidentCursorPagination(CursorPagination):
    page_size = 25
    page_size_query_param = 'limit'
    max_page_size = 200
    ordering = '-unique_date'


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IncidentSerializer
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (PaginatedCSVRenderer,)
    pagination_class = IncidentCursorPagination

    def get_serializer_class(self):
        if self.request.accepted_renderer.format == 'csv':
            return FlatIncidentSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        incident_filter = IncidentFilter(self.request.GET)
        incidents = incident_filter.get_queryset()

        return incidents.with_most_recent_update().with_public_associations()
