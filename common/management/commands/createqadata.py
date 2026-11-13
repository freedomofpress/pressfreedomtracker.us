from itertools import cycle

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from wagtail.models import Page, Site

import factory.random

from common.devdata import CategoryPageFactory, CommonTagFactory
from common.management.commands.createcategories import CATEGORIES
from common.models import (
    CategoryPage,
    GeneralIncidentFilter,
    IncidentFilterSettings,
    SearchSettings,
)
from home.models import HomePage
from home.tests.factories import HomePageFactory
from incident.devdata import IncidentIndexPageFactory, IncidentPageFactory


# Seed for factory_boy and Faker, so every run generates the same content.
SEED = "pressfreedomtracker-qa"

# Incidents created in each category.
INCIDENTS_PER_CATEGORY = 2

# The filters shown in the "General" section of the incident filter sidebar,
GENERAL_INCIDENT_FILTERS = [
    "date",
    "recently_updated",
    "city",
    "state",
    "targeted_journalists",
    "targeted_institutions",
    "tags",
    "case_number",
    "case_type",
    "case_statuses",
]

# Tags given to incidents, in turn, for the sidebar's tag filter.
TAGS = ["protest", "courthouse", "press pass"]


class Command(BaseCommand):
    help = (
        "Populate the database with the small, deterministic site that our "
        "Playwright QA test suite in e2e/ expects. This will tear down "
        "existing content before recreating it."
    )

    def get_home_page(self):
        return HomePage.objects.get(slug="home")

    def get_site(self):
        return Site.objects.get(is_default_site=True)

    def generate_home_page(self):
        self.stdout.write("Building home page")

        # Clear any prior default site & home page (Wagtail's welcome page on a
        # fresh DB, or our own home on a re-run) so this is idempotent.
        # Delete the site first to free the root_page FK.
        Site.objects.filter(is_default_site=True).delete()
        Page.objects.filter(slug="home").delete()

        root = Page.objects.filter(depth=1).first()
        if root is None:
            root = Page.add_root(instance=Page(title="Root"))

        home = HomePageFactory(
            parent=root,
            title="Home",
            slug="home",
            about=(
                "<p>A database of press freedom incidents in the United States.</p>"
            ),
        )

        Site.objects.create(
            root_page=home,
            hostname="localhost",
            port=8000,
            is_default_site=True,
            site_name="Press Freedom Tracker (QA)",
        )
        return home

    def generate_categories(self):
        self.stdout.write("Building category pages")
        home_page = self.get_home_page()

        return [
            CategoryPageFactory(
                parent=home_page,
                incident_filters=filters,
                viz_type="bar",
                **{trait: True},
            )
            for trait, filters in CATEGORIES.items()
        ]

    def generate_incidents(self):
        self.stdout.write("Building incidents")
        home_page = self.get_home_page()

        index = IncidentIndexPageFactory(
            parent=home_page,
            title="All Incidents",
            slug="all-incidents",
        )

        search_settings = SearchSettings.for_site(self.get_site())
        search_settings.search_page = index
        search_settings.save()

        tags = cycle([CommonTagFactory(title=title) for title in TAGS])
        for category in CategoryPage.objects.child_of(home_page):
            for incident in IncidentPageFactory.create_batch(
                INCIDENTS_PER_CATEGORY,
                parent=index,
                categories=[category],
            ):
                incident.tags.add(next(tags))
                incident.save()

        return index

    def generate_incident_filters(self):
        self.stdout.write("Configuring incident filters")
        settings = IncidentFilterSettings.for_site(self.get_site())
        GeneralIncidentFilter.objects.bulk_create(
            GeneralIncidentFilter(
                incident_filter_settings=settings,
                incident_filter=incident_filter,
                sort_order=i,
            )
            for i, incident_filter in enumerate(GENERAL_INCIDENT_FILTERS)
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Creating QA data... ", "")
        self.stdout.flush()

        factory.random.reseed_random(SEED)

        call_command("loaddata", "devuser", verbosity=0)

        # Generate the page tree and content
        self.generate_home_page()
        self.generate_categories()
        self.generate_incidents()
        self.generate_incident_filters()

        self.stdout.write(self.style.SUCCESS("Done"))
