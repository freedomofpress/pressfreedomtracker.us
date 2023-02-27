from django.core.management.base import BaseCommand
from django.db import transaction

from wagtail.models import Page

from common.devdata import (
    CategoryPageFactory,
    DevelopmentSiteFactory,
)
from common.tests.utils import make_html_string
from home.tests.factories import HomePageFactory


CATEGORIES = {
    # Note: the keys in this dictionary must match the parameter names
    # on the CategoryPageFactory class.
    'arrest': [
        'arrest_status',
        'arresting_authority',
        'status_of_charges',
        'detention_date',
        'release_date',
        'unnecessary_use_of_force',
        'charges',
    ],
    'border_stop': [
        'border_point',
        'stopped_at_border',
        'stopped_previously',
        'target_us_citizenship_status',
        'denial_of_entry',
        'target_nationality',
        'did_authorities_ask_for_device_access',
        'did_authorities_ask_for_social_media_user',
        'did_authorities_ask_for_social_media_pass',
        'did_authorities_ask_about_work',
        'were_devices_searched_or_seized',
    ],
    'denial_of_access': [
        'politicians_or_public_figures_involved',
    ],
    'equipment_search': [
        'equipment_seized',
        'status_of_seized_equipment',
        'is_search_warrant_obtained',
        'actor',
    ],
    'assault': [
        'assailant',
        'was_journalist_targeted',
    ],
    'leak_case': [
        'charged_under_espionage_act',
    ],
    'subpoena': [
        'legal_order_target',
        'legal_order_type',
        'legal_order_status',
        'legal_order_venue',
        'legal_order_information_requested',
        'third_party_business',
        'third_party_in_possession_of_communications',
    ],
    'equipment_damage': [
        'equipment_broken',
    ],
    'prior_restraint': [
        'status_of_prior_restraint',
    ],
    'chilling_statement': [],
    'other_incident': [],
}


class Command(BaseCommand):
    help = 'Creates categories appropriate for development'

    @transaction.atomic
    def handle(self, *args, **options):
        # Remove default wagtail home page, it's not needed.
        Page.objects.filter(slug='home').delete()

        root_page = Page.objects.get(slug='root')
        home_page = HomePageFactory(
            parent=root_page,
            about=make_html_string(),
        )
        DevelopmentSiteFactory(root_page=home_page)

        self.stdout.write('Creating categories', ending='')
        for trait, filters in CATEGORIES.items():
            CategoryPageFactory(
                parent=home_page,
                incident_filters=filters,
                **{trait: True}
            )
            self.stdout.write('.', ending='')

        self.stdout.write('')
