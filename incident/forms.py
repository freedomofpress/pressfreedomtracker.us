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
