# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-02-15 22:02
from __future__ import unicode_literals

from django.db import migrations
from wagtail.wagtailcore.models import Page, Site
from wagtail.wagtailcore.rich_text import RichText

from common.models import (
    CategoryPage,
    IncidentFieldCategoryPage,
    TaxonomyCategoryPage,
    TaxonomySettings
)
from home.models import HomePage


ARREST_FIELDS = [
    {
        'name': 'arrest_status',
        'type': 'choice'
    },
    {
        'name': 'status_of_charges',
        'type': 'choice'
    },
    {
        'name': 'detention_date',
        'type': 'date'
    },
    {
        'name': 'release_date',
        'type': 'date'
    },
    {
        'name': 'unnecessary_use_of_force',
        'category_slug': 'arrest-criminal-charge',
    }
]

LAWSUIT_FIELDS = [
    {
        'name': 'lawsuit_name',
        'type': 'char'
    },
    {
        'name': 'venue',
        'type': 'pk'
    }
]

EQUIPMENT_FIELDS = [
    {
        'name': 'equipment_seized',
        'modifier': 'equipment',
        'type': 'pk',
    },
    {
        'name': 'equipment_broken',
        'type': 'pk',
        'modifier': 'equipment',
    },
    {
        'name': 'status_of_seized_equipment',
        'type': 'choice',
    },
    {
        'name': 'is_search_warrant_obtained',
        'category_slug': 'equipment-search-seizure-or-damage'
    },
    {
        'name': 'actor',
        'type': 'choice',
    },
]

LEAK_PROSECUTIONS_FIELDS = [
    {
        'name': 'charged_under_espionage_act',
        'category_slug': 'leak-case',
    }
]

DENIAL_OF_ACCESS_FIELDS = [
    {
        'name': 'politicians_or_public_figures_involved',
        'type': 'pk',
    }
]

BORDER_STOP_FIELDS = [
    {
        'name': 'border_point',
        'type': 'char',
    },
    {
        'name': 'stopped_at_border',
        'category_slug': 'border-stop',
    },
    {
        'name': 'stopped_previously',
        'category_slug': 'border-stop',
    },
    {
        'name': 'target_us_citizenship_status',
        'type': 'choice',
    },
    {
        'name': 'denial_of_entry',
        'category_slug': 'border-stop',
    },
    {
        'name': 'target_nationality',
        'type': 'pk'
    },
    {
        'name': 'did_authorities_ask_for_device_access',
        'type': 'choice',
    },
    {
        'name': 'did_authorities_ask_for_social_media_user',
        'type': 'choice',
    },
    {
        'name': 'did_authorities_ask_for_social_media_pass',
        'type': 'choice',
    },
    {
        'name': 'did_authorities_ask_about_work',
        'type': 'choice',
    },
    {
        'name': 'were_devices_searched_or_seized',
        'type': 'choice',
    }
]

PHYSICAL_ASSAULT_FIELDS = [
    {
        'name': 'assailant',
        'type': 'choice',
    },
    {
        'name': 'was_journalist_targeted',
        'type': 'choice',
    },
]

SUBPOENA_FIELDS = [
    {
        'name': 'subpoena_type',
        'type': 'choice',
    },
    {
        'name': 'subpoena_status',
        'type': 'choice',
    },
    {
        'name': 'held_in_contempt',
        'type': 'choice',
    },
    {
        'name': 'detention_status',
        'type': 'choice',
    },
]

LEGAL_ORDER_FIELDS = [
    {
        'name': 'third_party_in_possession_of_communications',
        'type': 'char',
    },
    {
        'name': 'third_party_business',
        'type': 'choice',
    },
    {
        'name': 'legal_order_type',
        'type': 'choice',
    },

]

PRIOR_RESTRAINT_FIELDS = [
    {
        'name': 'status_of_prior_restraint',
        'type': 'choice',
    },
]

CATEGORIES = {
    'Arrest / Criminal Charge': ARREST_FIELDS,
    'Border Stop': BORDER_STOP_FIELDS,
    'Denial of Access': DENIAL_OF_ACCESS_FIELDS,
    'Equipment Search or Seizure': EQUIPMENT_FIELDS,
    'Leak Case': LEAK_PROSECUTIONS_FIELDS,
    'Physical Attack': PHYSICAL_ASSAULT_FIELDS,
    'Subpoena / Legal Order': SUBPOENA_FIELDS,
}


def create_initial_category_fields(apps, schema_editor):
    if not HomePage.objects.filter(slug='home'):
        root_page = Page.objects.get(title='Root')
        # Delete the default home page
        Page.objects.get(slug='home').delete()
        home_page = HomePage(
            title='Home',
            slug='home',
            about=RichText('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut in erat orci. Pellentesque eget scelerisque felis, ut iaculis erat. Nullam eget quam felis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Vestibulum eu dictum ligula. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Praesent et mi tellus. Suspendisse bibendum mi vel ex ornare imperdiet. Morbi tincidunt ut nisl sit amet fringilla. Proin nibh nibh, venenatis nec nulla eget, cursus finibus lectus. Aenean nec tellus eget sem faucibus ultrices.'),
        )
        root_page.add_child(instance=home_page)
    else:
        home_page = HomePage.objects.get(slug='home')

    if not Site.objects.filter(is_default_site=True):
        site = Site.objects.create(
            site_name='Press Freedom Incidents (Dev)',
            hostname='localhost',
            port='8000',
            root_page=home_page,
            is_default_site=True
        )
    else:
        site = Site.objects.get(
            is_default_site=True,
        )

    taxonomy_settings = TaxonomySettings.for_site(site)

    counter = 1
    for title, fields in CATEGORIES.items():
        category = CategoryPage.objects.filter(title=title).first()
        if not category:
            category = CategoryPage(title=title)
            home_page.add_child(instance=category)

        for field in fields:
            IncidentFieldCategoryPage.objects.get_or_create(
                category=category,
                incident_field=field['name']
            )
        TaxonomyCategoryPage.objects.create(
            sort_order=counter,
            taxonomy_setting=taxonomy_settings,
            category=category,
        )
        counter += 1


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0035_auto_20180215_2149'),
        ('home', '0020_remove_homepage_incident_index_page'),
        ('forms', '0003_formpage_search_image'),
        ('blog', '0015_auto_20180208_0024'),
        ('incident', '0023_auto_20180215_2149'),
        ('menus', '0001_initial'),
        ('wagtailforms', '0001_initial')
    ]

    operations = [
        migrations.RunPython(create_initial_category_fields)
    ]
