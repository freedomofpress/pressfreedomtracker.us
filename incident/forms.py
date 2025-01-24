from wagtail.admin.forms import WagtailAdminPageForm

from django import forms


class TopicPageForm(WagtailAdminPageForm):
    def clean(self):
        cleaned_data = super().clean()

        if (
            cleaned_data['start_date'] and
            cleaned_data['end_date'] and
            cleaned_data['start_date'] > cleaned_data['end_date']
        ):
            self.add_error(
                'start_date',
                'The start date cannot be after the end date.'
            )


class LegalOrderImportForm(forms.Form):
    csv_file = forms.FileField()
