from django import forms
from django.utils.text import capfirst

from wagtailautocomplete.widgets import Autocomplete

from common.models import CommonTag


class BaseMergeForm(forms.Form):
    title_for_merged_models = title_for_merged_models = forms.CharField(
        max_length=255,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.merge_model_name = self.merge_model._meta.verbose_name_plural

        self.fields['models_to_merge'] = forms.models.ModelMultipleChoiceField(
            queryset=self.merge_model.objects.all(),
            widget=Autocomplete(
                target_model=self.merge_model,
                can_create=False,
                is_single=False
            ),
            label='{} to merge'.format(capfirst(self.merge_model_name))
        )

        self.fields['title_for_merged_models'].label = 'Title for merged {}'.format(self.merge_model_name)


class TagMergeForm(BaseMergeForm):
    merge_model = CommonTag
