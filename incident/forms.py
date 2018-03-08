from django import forms
from incident.models import Target, Nationality, Venue
from autocomplete.widgets import Autocomplete


class TargetMergeForm(forms.Form):
    merge_model = Target
    merge_model_type = 'incident.Target'
    merge_model_name = 'targets'
    models_to_merge = forms.models.ModelMultipleChoiceField(
        queryset=merge_model.objects.all(),
        widget=type(
            '_Autocomplete',
            (Autocomplete,),
            dict(page_type=merge_model_type, can_create=False, is_single=False)
        ),
        label='Fields to merge'
    )
    title_for_merged_models = forms.CharField(max_length=255, label='Title for merged {}'.format(merge_model_name))


class NationalityMergeForm(forms.Form):
    merge_model = Nationality
    merge_model_type = 'incident.Nationality'
    merge_model_name = 'nationalities'
    models_to_merge = forms.models.ModelMultipleChoiceField(
        queryset=merge_model.objects.all(),
        widget=type(
            '_Autocomplete',
            (Autocomplete,),
            dict(page_type=merge_model_type, can_create=False, is_single=False)
        ),
        label='Fields to merge'
    )
    title_for_merged_models = forms.CharField(max_length=255, label='Title for merged {}'.format(merge_model_name))


class VenueMergeForm(forms.Form):
    merge_model = Venue
    merge_model_type = 'incident.Venue'
    merge_model_name = 'venues'
    models_to_merge = forms.models.ModelMultipleChoiceField(
        queryset=merge_model.objects.all(),
        widget=type(
            '_Autocomplete',
            (Autocomplete,),
            dict(page_type=merge_model_type, can_create=False, is_single=False)
        ),
        label='Fields to merge'
    )
    title_for_merged_models = forms.CharField(max_length=255, label='Title for merged {}'.format(merge_model_name))
