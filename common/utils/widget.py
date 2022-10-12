from django.forms.widgets import HiddenInput, SelectDateWidget


class YearWidget(SelectDateWidget):
    def __init__(self, isEndOfYear=False, *args, **kwargs):
        self.isEndOfYear = isEndOfYear
        return super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        day_name = self.day_field % name
        day_subwidget = HiddenInput().get_context(
            name=day_name,
            value=31 if self.isEndOfYear else 1,
            attrs={**context["widget"]["attrs"], "id": "id_%s" % day_name},
        )
        month_name = self.month_field % name
        month_subwidget = HiddenInput().get_context(
            name=month_name,
            value=12 if self.isEndOfYear else 1,
            attrs={**context["widget"]["attrs"], "id": "id_%s" % month_name},
        )
        context["widget"]["subwidgets"][0] = day_subwidget["widget"]
        context["widget"]["subwidgets"][1] = month_subwidget["widget"]

        return context

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        if y == "":
            return None

        value = super().value_from_datadict(data, files, name)
        return value
