import datetime
import json

from django.db import models

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page, Site

from modelcluster.fields import ParentalKey
from wagtailautocomplete.edit_handlers import AutocompletePanel

from common.models import MediaPageMixin, MetadataPageMixin
from common.models.settings import SearchSettings
from incident.models import (
    PrepublicationIncident,
    PrepublicationIncidentSync,
    PrepublicationSettings,
)
from incident.utils.incident_filter import get_serialized_filters


class HomePage(MetadataPageMixin, MediaPageMixin, Page):
    about = RichTextField(
        blank=True, null=True, help_text="Headings and line breaks will be stripped"
    )

    about_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    blog_index_page = models.ForeignKey(
        "blog.BlogIndexPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Recent blog posts will automatically be pulled from this page",
    )

    featured_incidents_label = models.CharField(
        default="Featured Incidents",
        max_length=255,
        help_text="Title displayed above featured pages",
    )

    featured_incidents_more_label = models.CharField(
        default="Go to Incidents Database",
        max_length=255,
        help_text="Text for button show more incidents",
    )

    recent_incidents_label = models.CharField(
        default="Recent Incidents",
        max_length=255,
        help_text="Title displayed above recent incidents",
    )

    recent_incidents_count = models.PositiveIntegerField(
        default=8,
        null=True,
        help_text="Number of recent incidents to display",
    )

    recent_incidents_more_label = models.CharField(
        default="Go to Incidents Database",
        max_length=255,
        help_text="Text for button to show more recent incidents",
    )

    featured_blog_posts_label = models.CharField(
        default="From Our Blog",
        max_length=255,
        help_text="Title displayed above blog posts",
    )

    featured_blog_posts_more_label = models.CharField(
        default="Go to Blog",
        max_length=255,
        help_text="Text for button to show more blog posts",
    )
    categories_label = models.CharField(
        default="Learn More About Our Categories",
        max_length=255,
        help_text="Title displayed above categories",
    )
    categories_body = models.TextField(
        help_text="Paragraph of extra information about categories",
        blank=True,
    )

    # Data Viz Configuration
    viz_data_start = models.DateField(
        "Start Date",
        blank=True,
        null=True,
    )
    viz_data_end = models.DateField(
        "End Date",
        blank=True,
        null=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("about"),
                PageChooserPanel(
                    "about_page", ["common.SimplePage", "common.SimplePageWithSidebar"]
                ),
            ],
            "About",
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                PageChooserPanel("blog_index_page", "blog.BlogIndexPage"),
                InlinePanel("featured_blog_posts", max_num=6),
                FieldPanel("featured_blog_posts_label"),
                FieldPanel("featured_blog_posts_more_label"),
            ],
            "Featured Blog Posts",
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    "featured_incidents", heading="Featured Incidents", max_num=6
                ),
                FieldPanel("featured_incidents_label"),
                FieldPanel("featured_incidents_more_label"),
            ],
            "Featured Incidents",
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                FieldPanel("categories_label"),
                FieldPanel("categories_body"),
            ],
            "Categories",
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                FieldPanel("recent_incidents_label"),
                FieldPanel("recent_incidents_count"),
                FieldPanel("recent_incidents_more_label"),
            ],
            "Recent Incidents",
            classname="collapsible",
        ),
    ]

    data_viz_panels = [
        InlinePanel("data_viz_tags", heading="Tag Options"),
        # A bit of a visual hack--wrapping a FieldRowPanel in a MultiFieldPanel
        # makes the FieldRowPanel a more reasonable width in the interface
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("viz_data_start"),
                        FieldPanel("viz_data_end"),
                    ],
                    classname="label-above",
                )
            ],
            heading="Limit Data",
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(data_viz_panels, heading="Data Viz"),
            ObjectList(MetadataPageMixin.promote_panels, heading="Promote"),
            ObjectList(Page.settings_panels, heading="Settings"),
        ]
    )

    def get_context(self, request, *args, **kwargs):
        context = super(HomePage, self).get_context(request, *args, **kwargs)

        context["serialized_filters"] = json.dumps(get_serialized_filters())

        context["featured_blog_posts"] = [
            f.page for f in self.featured_blog_posts.select_related("page")
        ]

        context["featured_incident_pages"] = [
            f.page
            for f in self.featured_incidents.select_related(
                "page",
                "page__teaser_image",
            )
        ]

        context["data_viz_tags_json"] = json.dumps(
            [t.tag.title for t in self.data_viz_tags.all()]
        )

        search_settings = SearchSettings.for_site(Site.find_for_request(request))

        if search_settings.data_download_page:
            context["export_path"] = (
                search_settings.data_download_page.get_url()
            )  # pragma: no cover
        elif search_settings.search_page:
            context["export_path"] = (
                search_settings.search_page.get_url()
                + search_settings.search_page.reverse_subpage("export_view")
            )  # pragma: no cover
        else:
            context["export_path"] = None

        prepub_settings = PrepublicationSettings.load(request_or_site=request)
        sync = PrepublicationIncidentSync.objects.first()
        if prepub_settings.is_enabled and sync:
            lower_date = datetime.date.today() - prepub_settings.get_timespan()
            context["prepubs"] = (
                PrepublicationIncident.objects.aggregate_with_category_counts(
                    lower_date_bound=lower_date,
                )
            )
            context["prepub_count"] = PrepublicationIncident.objects.fuzzy_date_filter(
                lower=lower_date, upper=datetime.date.today()
            ).count()
            context["update_time"] = sync.completed_at.strftime("%H:%M %p %Z")
            context["timespan_display"] = prepub_settings.get_timespan_display()

        return context


class FeaturedIncident(Orderable):
    home_page = ParentalKey("home.HomePage", related_name="featured_incidents")
    page = models.ForeignKey(
        "incident.IncidentPage", on_delete=models.CASCADE, related_name="+"
    )

    panels = [
        FieldPanel("page"),
    ]


class FeaturedBlogPost(Orderable):
    home_page = ParentalKey("home.HomePage", related_name="featured_blog_posts")
    page = models.ForeignKey(
        "blog.BlogPage", on_delete=models.CASCADE, related_name="+"
    )

    panels = [
        FieldPanel("page"),
    ]


class DataVizTag(Orderable):
    home_page = ParentalKey("home.HomePage", related_name="data_viz_tags")
    tag = ParentalKey("common.CommonTag")

    panels = [
        AutocompletePanel("tag", "common.CommonTag"),
    ]
