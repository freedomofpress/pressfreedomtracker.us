from common.forms import BaseMergeForm
from incident.models import Target, Charge, Nationality, Venue, PoliticianOrPublic, Journalist


class TargetMergeForm(BaseMergeForm):
    merge_model = Target
    merge_model_type = 'incident.Target'


class JournalistMergeForm(BaseMergeForm):
    merge_model = Journalist
    merge_model_type = 'incident.Journalist'


class ChargeMergeForm(BaseMergeForm):
    merge_model = Charge
    merge_model_type = 'incident.Charge'


class NationalityMergeForm(BaseMergeForm):
    merge_model = Nationality
    merge_model_type = 'incident.Nationality'


class VenueMergeForm(BaseMergeForm):
    merge_model = Venue
    merge_model_type = 'incident.Venue'


class PoliticianOrPublicMergeForm(BaseMergeForm):
    merge_model = PoliticianOrPublic
    merge_model_type = 'incident.PoliticianOrPublic'
