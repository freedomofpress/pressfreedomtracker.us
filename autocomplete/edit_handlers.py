from wagtail.wagtailadmin.edit_handlers import BaseFieldPanel

from .widgets import Autocomplete


class AutocompleteFieldPanel:
    def __init__(self, field_name, page_type='wagtailcore.Page'):
        self.field_name = field_name
        self.page_type = page_type

    def bind_to_model(self, model):
        base = dict(
            model=model,
            field_name=self.field_name,
            widget=type(
                '_Autocomplete',
                (Autocomplete,),
                dict(page_type=self.page_type),
            ),
        )
        return type('_AutocompleteFieldPanel', (BaseFieldPanel,), base)
