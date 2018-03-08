from common.views import MergeView
from incident.forms import TargetMergeForm, VenueMergeForm, NationalityMergeForm

class TargetMergeView(MergeView):
    form_class = TargetMergeForm
    filter_name = 'targets'


class NationalityMergeView(MergeView):
    form_class = NationalityMergeForm
    filter_name = 'target_nationality'
    related_name = 'nationality_incidents'


class VenueMergeView(MergeView):
    form_class = VenueMergeForm
    filter_name = 'venue'
    related_name = 'venue_incidents'
