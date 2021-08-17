from wagtail.admin.forms import WagtailAdminPageForm

from common.forms import BaseMergeForm
from incident.models import Charge, Nationality, Venue, PoliticianOrPublic, Journalist, Institution, GovernmentWorker, LawEnforcementOrganization


class JournalistMergeForm(BaseMergeForm):
    merge_model = Journalist


class InstitutionMergeForm(BaseMergeForm):
    merge_model = Institution


class ChargeMergeForm(BaseMergeForm):
    merge_model = Charge


class LawEnforcementOrganizationForm(BaseMergeForm):
    merge_model = LawEnforcementOrganization


class NationalityMergeForm(BaseMergeForm):
    merge_model = Nationality


class VenueMergeForm(BaseMergeForm):
    merge_model = Venue


class PoliticianOrPublicMergeForm(BaseMergeForm):
    merge_model = PoliticianOrPublic


class GovernmentWorkerMergeForm(BaseMergeForm):
    merge_model = GovernmentWorker


class TopicPageForm(WagtailAdminPageForm):
    def clean(self):
        cleaned_data = super().clean()

        if (
            cleaned_data['start_date'] and
            cleaned_data['end_date'] and
            cleaned_data['start_date'] > cleaned_data['end_date']
        ):
            self.add_error(
                'start_date',
                'The start date cannot be after the end date.'
            )
