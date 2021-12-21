import datetime

from django.views.generic import TemplateView

from common.devdata import CommonTagFactory
from incident.devdata import MultimediaIncidentPageFactory, InstitutionFactory, TargetedJournalistFactory, IncidentCategorizationFactory


class StyleguideView(TemplateView):
    template_name = 'styleguide/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create sample incident for the styleguide without touching
        # the database.
        inc = MultimediaIncidentPageFactory.build()
        inc.latest_update = datetime.datetime.utcnow()
        inc.tags = CommonTagFactory.build_batch(5)
        inc.targeted_institutions = InstitutionFactory.build_batch(2)
        inc.targeted_journalists = TargetedJournalistFactory.build_batch(
            2,
            # We are creating the incident relationship using
            # modelcluster directly, tell the factory not to generate
            # an incident.
            incident=None,
        )
        inc.categories = IncidentCategorizationFactory.build_batch(
            2,
            # We are creating the incident relationship using
            # modelcluster directly, tell the factory not to generate
            # an incident.
            incident_page=None,
        )
        context['incident'] = inc

        return context