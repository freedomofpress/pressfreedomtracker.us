from django import forms
from common.models import CommonTag

from autocomplete.widgets import Autocomplete


class TagMergeForm(forms.Form):
    merge_model = CommonTag
    merge_model_type = 'common.CommonTag'
    merge_model_name = 'tags'
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
