from common.views import MergeView
from incident.forms import TargetMergeForm, ChargeMergeForm, VenueMergeForm, NationalityMergeForm, PoliticianOrPublicMergeForm


class TargetMergeView(MergeView):
    form_class = TargetMergeForm


class ChargeMergeView(MergeView):
    form_class = ChargeMergeForm


class NationalityMergeView(MergeView):
    form_class = NationalityMergeForm


class VenueMergeView(MergeView):
    form_class = VenueMergeForm


class PoliticianOrPublicMergeView(MergeView):
    form_class = PoliticianOrPublicMergeForm
