from common.forms import BaseMergeForm
from incident.models import Charge, Nationality, Venue,PoliticianOrPublic, Journalist, Institution, GovernmentWorker, LawEnforcementOrganization


class JournalistMergeForm(BaseMergeForm):
    merge_model = Journalist
    merge_model_type = 'incident.Journalist'


class InstitutionMergeForm(BaseMergeForm):
    merge_model = Institution
    merge_model_type = 'incident.Institution'


class ChargeMergeForm(BaseMergeForm):
    merge_model = Charge
    merge_model_type = 'incident.Charge'


class LawEnforcementOrganizationForm(BaseMergeForm):
    merge_model = LawEnforcementOrganization
    merge_model_type = 'incident.LawEnforcementOrganization'


class NationalityMergeForm(BaseMergeForm):
    merge_model = Nationality
    merge_model_type = 'incident.Nationality'


class VenueMergeForm(BaseMergeForm):
    merge_model = Venue
    merge_model_type = 'incident.Venue'


class PoliticianOrPublicMergeForm(BaseMergeForm):
    merge_model = PoliticianOrPublic
    merge_model_type = 'incident.PoliticianOrPublic'


class GovernmentWorkerMergeForm(BaseMergeForm):
    merge_model = GovernmentWorker
    merge_model_type = 'incident.GovernmentWorker'
