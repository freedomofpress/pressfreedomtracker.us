from django.db import models
from rest_framework import viewsets

from incident.models import IncidentPage, TargetedJournalist
from incident.api.serializers import IncidentSerializer


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IncidentSerializer

    def get_queryset(self):
        return IncidentPage.objects.all()\
            .with_most_recent_update() \
            .select_related('teaser_image', 'state', 'arresting_authority') \
            .prefetch_related(
                'authors__author',
                'categories__category',
                'current_charges',
                'dropped_charges',
                'equipment_broken__equipment',
                'equipment_seized__equipment',
                'links',
                'politicians_or_public_figures_involved',
                'tags',
                'target_nationality',
                'targeted_institutions',
                models.Prefetch('targeted_journalists', queryset=TargetedJournalist.objects.select_related('journalist', 'institution')),
                'teaser_image__renditions',
                'updates',
                'venue',
                'workers_whose_communications_were_obtained',
        )
