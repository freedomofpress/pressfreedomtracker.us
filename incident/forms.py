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


class IncidentPageForm(WagtailAdminPageForm):
    def clean(self):
        cleaned_data = super().clean()
        if self.is_deferred_validation:
            return cleaned_data

        if cleaned_data.get("externally_reported"):
            if not self._has_external_reports():
                self.add_error(
                    "externally_reported",
                    "Add at least one external report for an incident that relies on external reporting.",
                )
        elif not cleaned_data.get("body"):
            self.add_error("body", forms.Field.default_error_messages["required"])
        return cleaned_data

    def _has_external_reports(self):
        reports = self.formsets["external_reports"]
        # Formsets are cleaned after the parent form, so force it here.
        reports.is_valid()
        return any(
            form.cleaned_data and not form.cleaned_data.get("DELETE")
            for form in reports.forms
        )


class LegalOrderImportForm(forms.Form):
    csv_file = forms.FileField()
