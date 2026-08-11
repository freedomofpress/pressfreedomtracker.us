from django.urls import path, re_path

import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.admin.panels import FieldPanel
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineEntityElementHandler,
)
from wagtail.admin.rich_text.editors.draftail.features import PluginFeature
from wagtail.admin.ui.tables import Column
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.rich_text.pages import PageLinkHandler
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from draftjs_exporter.dom import DOM
from taggit.models import Tag, TaggedItem
from django.templatetags.static import static

from .models import CategoryPage, CommonTag
from .views import MailchimpInterestsView, check_chart_health, deploy_info_view


class CategoryPageLinkHandler(PageLinkHandler):
    """Class to apply CSS to links to CategoryPages in rich text"""

    identifier = "page"

    @classmethod
    def expand_db_attributes_many(cls, attrs_list: list[dict]) -> list[str]:
        links = super().expand_db_attributes_many(attrs_list)

        results = []
        for link, attrs in zip(links, attrs_list):
            try:
                page = CategoryPage.objects.get(pk=attrs["id"])
                results.append(
                    link.replace(
                        "<a",
                        f'<a class="category category-{page.page_symbol}"',
                    )
                )
            except CategoryPage.DoesNotExist:
                results.append(link)
        return results


@hooks.register("register_rich_text_features", order=10)
def register_external_link(features):
    features.register_link_type(CategoryPageLinkHandler)


class MergeAdmin(ModelViewSet):
    exclude_form_fields = []

    class Meta:
        abstract = True


class CommonTagAdmin(MergeAdmin):
    model = CommonTag
    menu_label = "Incident Tags"
    icon = "tag"
    menu_order = 400  # will put in 4th place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = (
        False  # or True to exclude pages of this type from Wagtail's explorer view
    )
    list_display = ("title", "incident_count")
    search_fields = ("title",)
    inspect_view_enabled = True
    inspect_view_fields = ("title",)


@hooks.register("register_admin_urls")
def urlconf_time():
    return [
        re_path(r"^version/?$", deploy_info_view, name="deployinfo"),
        path(
            "check_chart_health/",
            check_chart_health,
            name="check_chart_health",
        ),
    ]


@hooks.register("register_rich_text_features")
def register_num_incidents_feature(features):
    feature_name = "numincidents"
    type_ = "SEARCHSTAT"

    control = {
        "type": type_,
        "label": "Stats",
        "description": "Statistics data matching an incident search",
    }

    features.register_editor_plugin(
        "draftail",
        feature_name,
        draftail_features.EntityFeature(
            control,
            js=[static("bundles/statistics.js")],
            css={"all": [static("bundles/statistics.css")]},
        ),
    )

    features.register_converter_rule(
        "contentstate",
        feature_name,
        {
            "from_database_format": {
                'span[data-entity="num-incidents"]': SearchStatEntityElementHandler(
                    type_
                )
            },
            "to_database_format": {
                "entity_decorators": {type_: num_incidents_entity_decorator}
            },
        },
    )


def num_incidents_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the num_incidents entities into a span tag.
    """
    filters = {
        k.replace("param_", "data-param-").replace("_", "-"): v
        for k, v in props.items()
        if k.startswith("param_")
    }
    dataset = props.get("dataset", "")  # pragma: no cover
    filters["data-entity"] = "num-incidents"  # pragma: no cover
    filters["data-count"] = props.get("count", "0")  # pragma: no cover
    filters["data-search"] = props.get("search", "")  # pragma: no cover
    filters["data-dataset"] = dataset  # pragma: no cover

    if dataset == "TOTAL":  # pragma: no cover
        tag_name = "num_incidents"
    elif dataset == "JOURNALISTS":  # pragma: no cover
        tag_name = "num_journalist_targets"  # pragma: no cover
    elif dataset == "INSTITUTIONS":  # pragma: no cover
        tag_name = "num_institution_targets"
    else:  # pragma: no cover
        tag_name = ""

    tag = "{{% {tag_name} {args} %}}".format(
        tag_name=tag_name,
        args=" ".join(
            '{k}="{v}"'.format(k=k.replace("param_", ""), v=v)
            for k, v in props.items()
            if k.startswith("param_")
        ),
    )

    return DOM.create_element("span", filters, tag)  # pragma: no cover


@hooks.register("register_admin_urls")
def mailchimp_urls():
    return [
        path(
            "mailchimp_interests/",
            MailchimpInterestsView.as_view(),
            name="mailchimp_interests",
        )
    ]


@hooks.register("register_rich_text_features")
def register_curlify(features):
    feature_name = "curlify"
    features.default_features.append(feature_name)

    features.register_editor_plugin(
        "draftail",
        feature_name,
        PluginFeature(
            {
                "type": feature_name,
            },
            js=[
                static("bundles/draftail.js"),
            ],
        ),
    )


class SearchStatEntityElementHandler(InlineEntityElementHandler):
    """
    Database HTML to Draft.js ContentState.
    Converts the span tag into a SearchStat entity, with the right data.
    """

    mutability = "IMMUTABLE"

    def get_attribute_data(self, attrs):
        """
        Take values from the HTML element's attributes
        """
        return {
            k.replace("data-", "").replace("-", "_"): v for k, v in attrs.items()
        }  # pragma: no cover


class TagCountColumn(Column):
    """Represents the number of items tagged with this tag."""

    def get_value(self, instance):
        return TaggedItem.objects.filter(tag=instance).count()


class TagsSnippetViewSet(SnippetViewSet):
    panels = [FieldPanel("name")]  # only show the name field
    model = Tag
    icon = "tag"
    add_to_settings_menu = True
    menu_label = "Image Tags"
    menu_order = 800
    list_display = ["name", "slug", TagCountColumn("tagged item count")]
    search_fields = ("name",)


register_snippet(TagsSnippetViewSet)
