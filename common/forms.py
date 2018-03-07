from django import forms
from common.models import CommonTag

from autocomplete.widgets import Autocomplete
from autocomplete.edit_handlers import AutocompleteFieldPanel

class TagMergeForm(forms.Form):
    tags = forms.models.ModelMultipleChoiceField(
        queryset=CommonTag.objects.all(),
        widget=type(
            '_Autocomplete',
            (Autocomplete,),
            dict(page_type='common.CommonTag', can_create=False, is_single=False)
        ),
        label='Fields to merge'
    )
    title_for_merged_tags = forms.CharField(max_length=255)
