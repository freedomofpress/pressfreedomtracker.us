from django.urls import re_path
from django.urls import reverse, path, include
from wagtail.contrib.modeladmin.options import (
    ModelAdminGroup,
    modeladmin_register,
)
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from wagtail.admin.search import SearchArea
from wagtail import hooks

from common.wagtail_hooks import MergeAdmin
from incident.models import (
    Journalist,
    Charge,
    Nationality,
    PoliticianOrPublic,
    Venue,
    Institution,
    LawEnforcementOrganization,
    GovernmentWorker,
)
from incident.views import (
    ChargeMergeView,
    incident_admin_search_view,
    NationalityMergeView,
    PoliticianOrPublicMergeView,
    VenueMergeView,
    JournalistMergeView,
    InstitutionMergeView,
    LawEnforcementOrganizationMergeView,
    GovernmentWorkerMergeView,
    LegalOrderImportView,
    LegalOrderImportConfirmView,
)


@hooks.register('register_admin_urls')
def incident_admin_search_url():
    return [
        re_path(r'^incident-search/$', incident_admin_search_view, name='incident-admin-search'),
    ]


@hooks.register('register_admin_urls')
def incident_legal_order_import_url():
    return [
        path(
            'legal_orders/',
            include(
                (
                    [
                        path(
                            'import/',
                            LegalOrderImportView.as_view(),
                            name='show_form',
                        ),
                        path(
                            'confirm/',
                            LegalOrderImportConfirmView.as_view(),
                            name='confirm',
                        ),
                        # path(
                        #     'success/',
                        #     TemplateView.as_view(template_name='....'),
                        #     name='success',
                        # ),
                    ],
                    'import_legal_orders',
                ),
                namespace='import_legal_orders',
            )
        ),
    ]


@hooks.register('register_admin_menu_item')
def register_tools_menu_item():
    legal_order_import_item = MenuItem(
        'Import Legal Orders',
        reverse('import_legal_orders:show_form'),
        classnames='icon icon-table'
    )
    mc_groups_item = MenuItem(
        'Mailchimp Groups',
        reverse('mailchimp_interests'),
        classnames='icon icon-mail',
        order=10,
    )

    submenu = Menu(
        items=[
            legal_order_import_item,
            mc_groups_item,
        ],
    )
    return SubmenuMenuItem('Tools', submenu, icon_name='code', order=10000)


@hooks.register('register_admin_search_area')
def incident_admin_search_area():
    return SearchArea(
        label='Incidents',
        url=reverse('incident-admin-search'),
        order=0,
    )


class GovernmentWorkerAdmin(MergeAdmin):
    model = GovernmentWorker
    merge_view_class = GovernmentWorkerMergeView
    menu_label = 'Alleged Recipients of Leaks'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class JournalistAdmin(MergeAdmin):
    model = Journalist
    merge_view_class = JournalistMergeView
    menu_label = 'Journalist'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class InstitutionAdmin(MergeAdmin):
    model = Institution
    merge_view_class = InstitutionMergeView
    menu_label = 'Institution'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class ChargeAdmin(MergeAdmin):
    model = Charge
    merge_view_class = ChargeMergeView
    menu_label = 'Charges'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class LawEnforcementOrganizationAdmin(MergeAdmin):
    model = LawEnforcementOrganization
    merge_view_class = LawEnforcementOrganizationMergeView
    menu_label = 'Law Enforcement Authorities'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class NationalityAdmin(MergeAdmin):
    model = Nationality
    merge_view_class = NationalityMergeView
    menu_label = 'Nationalities'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class PoliticianOrPublicAdmin(MergeAdmin):
    model = PoliticianOrPublic
    merge_view_class = PoliticianOrPublicMergeView
    menu_label = 'Politicians / Public Figures'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class VenueAdmin(MergeAdmin):
    model = Venue
    merge_view_class = VenueMergeView
    menu_label = 'Venues'
    menu_icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class IncidentGroup(ModelAdminGroup):
    menu_label = 'Incident M2Ms'
    menu_icon = 'folder-open-inverse'  # change as required
    menu_order = 600  # will put in 7th place (000 being 1st, 100 2nd)
    items = (ChargeAdmin, LawEnforcementOrganizationAdmin, NationalityAdmin, PoliticianOrPublicAdmin, VenueAdmin, JournalistAdmin, InstitutionAdmin, GovernmentWorkerAdmin)


modeladmin_register(IncidentGroup)
