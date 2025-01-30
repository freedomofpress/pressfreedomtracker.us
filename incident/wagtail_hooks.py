from django.urls import reverse, path, include
from wagtail.admin.viewsets.model import ModelViewSetGroup
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
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
    LegalOrderImportView,
    LegalOrderImportConfirmView,
)


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
        classname='icon icon-table'
    )
    mc_groups_item = MenuItem(
        'Mailchimp Groups',
        reverse('mailchimp_interests'),
        classname='icon icon-mail',
        order=10,
    )

    submenu = Menu(
        items=[
            legal_order_import_item,
            mc_groups_item,
        ],
    )
    return SubmenuMenuItem('Tools', submenu, icon_name='code', order=10000)


class GovernmentWorkerAdmin(MergeAdmin):
    model = GovernmentWorker
    menu_label = 'Alleged Recipients of Leaks'
    icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class JournalistAdmin(MergeAdmin):
    model = Journalist
    menu_label = 'Journalist'
    icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class InstitutionAdmin(MergeAdmin):
    model = Institution
    menu_label = 'Institution'
    icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class ChargeAdmin(MergeAdmin):
    model = Charge
    menu_label = 'Charges'
    icon = 'edit'
    list_display = ('title',)
    search_fields = ('title',)


class LawEnforcementOrganizationAdmin(MergeAdmin):
    model = LawEnforcementOrganization
    menu_label = 'Law Enforcement Authorities'
    icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class NationalityAdmin(MergeAdmin):
    model = Nationality
    menu_label = 'Nationalities'
    icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class PoliticianOrPublicAdmin(MergeAdmin):
    model = PoliticianOrPublic
    menu_label = 'Politicians / Public Figures'
    icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class VenueAdmin(MergeAdmin):
    model = Venue
    menu_label = 'Venues'
    icon = 'edit'
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title',)
    search_fields = ('title',)


class IncidentGroup(ModelViewSetGroup):
    menu_label = 'Incident M2Ms'
    icon = 'folder-open-inverse'  # change as required
    menu_order = 600  # will put in 7th place (000 being 1st, 100 2nd)
    items = (ChargeAdmin, LawEnforcementOrganizationAdmin, NationalityAdmin, PoliticianOrPublicAdmin, VenueAdmin, JournalistAdmin, InstitutionAdmin, GovernmentWorkerAdmin)


@hooks.register('register_admin_viewset')
def register_incidentgroup_viewset():
    return IncidentGroup()
