from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from wagtail.contrib.modeladmin.helpers import AdminURLHelper, ButtonHelper
from django.utils.translation import ugettext as _
from .models import CommonTag

class ButtonHelperWithMerge(ButtonHelper):
    merge_button_classnames = []

    def merge_button(self, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.add_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': self.url_helper.create_url,
            'label': _('Merge %s') % self.verbose_name,
            'classname': cn,
            'title': _('Merge %s') % self.verbose_name,
        }


class CommonTagAdmin(ModelAdmin):
    model = CommonTag
    button_helper_class = ButtonHelperWithMerge
    index_template_name = 'modeladmin/index_with_merge.html'
    menu_label = 'Tags'
    menu_icon = 'tag'
    menu_order = 500  # will put in 4th place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)

modeladmin_register(CommonTagAdmin)

