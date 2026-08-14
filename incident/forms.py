from django import forms

from wagtail.admin.forms import WagtailAdminPageForm


class TopicPageForm(WagtailAdminPageForm):
    def clean(self):
        cleaned_data = super().clean()

        if (
            cleaned_data["start_date"]
            and cleaned_data["end_date"]
            and cleaned_data["start_date"] > cleaned_data["end_date"]
        ):
            self.add_error(
                "start_date", "The start date cannot be after the end date."
            )  # pragma: no cover


class LegalOrderImportForm(forms.Form):
    csv_file = forms.FileField()
