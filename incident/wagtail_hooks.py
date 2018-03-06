from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)

from incident.models import Target, Charge, Nationality, PoliticianOrPublic, Venue

class TargetAdmin(ModelAdmin):
    model = Target
    menu_label = 'Targets'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)

class ChargeAdmin(ModelAdmin):
    model = Charge
    menu_label = 'Charges'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)

class NationalityAdmin(ModelAdmin):
    model = Nationality
    menu_label = 'Nationalities'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)

class PoliticianOrPublicAdmin(ModelAdmin):
    model = PoliticianOrPublic
    menu_label = 'Politicians / Public Figures'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)

class VenueAdmin(ModelAdmin):
    model = Venue
    menu_label = 'Venues'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)

class IncidentGroup(ModelAdminGroup):
    menu_label = 'Incident M2Ms'
    menu_icon = 'folder-open-inverse'  # change as required
    menu_order = 600  # will put in 7th place (000 being 1st, 100 2nd)
    items = (TargetAdmin, ChargeAdmin, NationalityAdmin, PoliticianOrPublicAdmin, VenueAdmin)

modeladmin_register(IncidentGroup)
