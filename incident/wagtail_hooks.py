from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)

from incident.models import Target, Charge, Nationality, PoliticianOrPublic, Venue
from common.wagtail_hooks import MergeAdmin
from incident.views import TargetMergeView, NationalityMergeView, VenueMergeView, PoliticianOrPublicMergeView


class TargetAdmin(MergeAdmin):
    model = Target
    merge_view_class = TargetMergeView
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


class NationalityAdmin(MergeAdmin):
    model = Nationality
    merge_view_class = NationalityMergeView
    menu_label = 'Nationalities'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)

class PoliticianOrPublicAdmin(MergeAdmin):
    model = PoliticianOrPublic
    merge_view_class = PoliticianOrPublicMergeView
    menu_label = 'Politicians / Public Figures'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)

class VenueAdmin(MergeAdmin):
    model = Venue
    merge_view_class = VenueMergeView
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
