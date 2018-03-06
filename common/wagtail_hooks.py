from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from .models import CommonTag

class CommonTagAdmin(ModelAdmin):
  model = CommonTag
  menu_label = 'Tags'
  menu_icon = 'tag'
  menu_order = 500  # will put in 4th place (000 being 1st, 100 2nd)
  add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
  exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
  list_display = ('title',)
  search_fields = ('title',)

modeladmin_register(CommonTagAdmin)

