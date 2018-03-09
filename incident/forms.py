from django import forms

from common.forms import BaseMergeForm
from incident.models import Target, Charge, Nationality, Venue, PoliticianOrPublic
from autocomplete.widgets import Autocomplete


class TargetMergeForm(BaseMergeForm):
    merge_model = Target
    merge_model_type = 'incident.Target'
    merge_model_name = 'targets'


class ChargeMergeForm(BaseMergeForm):
    merge_model = Charge
    merge_model_type = 'incident.Charge'
    merge_model_name = 'charges'


class NationalityMergeForm(BaseMergeForm):
    merge_model = Nationality
    merge_model_type = 'incident.Nationality'
    merge_model_name = 'nationalities'


class VenueMergeForm(BaseMergeForm):
    merge_model = Venue
    merge_model_type = 'incident.Venue'
    merge_model_name = 'venues'


class PoliticianOrPublicMergeForm(BaseMergeForm):
    merge_model = PoliticianOrPublic
    merge_model_type = 'incident.PoliticianOrPublic'
    merge_model_name = 'politician or public figure'
