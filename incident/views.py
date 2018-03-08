from common.views import MergeView
from incident.forms import TargetMergeForm, VenueMergeForm, NationalityMergeForm, PoliticianOrPublicMergeForm

class TargetMergeView(MergeView):
    form_class = TargetMergeForm
    filter_name = 'targets'


class NationalityMergeView(MergeView):
    form_class = NationalityMergeForm


class VenueMergeView(MergeView):
    form_class = VenueMergeForm


class PoliticianOrPublicMergeView(MergeView):
    form_class = PoliticianOrPublicMergeForm
