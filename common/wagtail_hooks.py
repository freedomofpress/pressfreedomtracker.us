import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from django.urls import re_path, path
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from draftjs_exporter.dom import DOM
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineEntityElementHandler
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail import hooks
from wagtail.rich_text.pages import PageLinkHandler
from webpack_loader.utils import get_files

from .models import CommonTag, CategoryPage
from .views import deploy_info_view, MailchimpInterestsView, check_chart_health


class CategoryPageLinkHandler(PageLinkHandler):
    """Class to apply CSS to links to CategoryPages in rich text"""
    identifier = 'page'

    @staticmethod
    def expand_db_attributes(attrs):
        # Defer to the superclass method for the HTML, then check if
        # the page we're linking to is a Category page.
        result = super(CategoryPageLinkHandler, CategoryPageLinkHandler).expand_db_attributes(attrs)

        try:
            page = CategoryPage.objects.get(pk=attrs['id'])
            return result.replace(
                '<a',
                f'<a class="category category-{page.page_symbol}"',
            )
        except CategoryPage.DoesNotExist:
            return result


@hooks.register('register_rich_text_features', order=10)
def register_external_link(features):
    features.register_link_type(CategoryPageLinkHandler)


class MergeAdmin(ModelViewSet):
    exclude_form_fields = []

    class Meta:
        abstract = True


class CommonTagAdmin(MergeAdmin):
    model = CommonTag
    menu_label = 'Tags'
    icon = 'tag'
    add_to_admin_menu = True
    menu_order = 400  # will put in 4th place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title', 'incident_count')
    search_fields = ('title',)
    inspect_view_enabled = True
    inspect_view_fields = ('title',)


@hooks.register("register_admin_viewset")
def register_viewset():
    return CommonTagAdmin()


@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        re_path(r'^version/?$', deploy_info_view, name='deployinfo'),
        path(
            'check_chart_health/',
            check_chart_health,
            name='check_chart_health',
        ),
    ]


@hooks.register('register_rich_text_features')
def register_num_incidents_feature(features):
    feature_name = 'numincidents'
    type_ = 'SEARCHSTAT'

    control = {
        'type': type_,
        'label': 'Stats',
        'description': 'Statistics data matching an incident search',
    }

    features.register_editor_plugin(
        'draftail', feature_name, draftail_features.EntityFeature(
            control,
            js=[get_files('statistics', extension='js')[0]['url']],
            css={'all': [get_files('statistics', extension='css')[0]['url']]}
        )
    )

    features.register_converter_rule('contentstate', feature_name, {
        'from_database_format': {'span[data-entity="num-incidents"]': SearchStatEntityElementHandler(type_)},
        'to_database_format': {'entity_decorators': {type_: num_incidents_entity_decorator}}
    })


def num_incidents_entity_decorator(props):
    """
    Draft.js ContentState to database HTML.
    Converts the num_incidents entities into a span tag.
    """
    filters = {
        k.replace('param_', 'data-param-').replace('_', '-'): v for k, v in props.items() if k.startswith('param_')
    }
    dataset = props.get('dataset', '')
    filters['data-entity'] = 'num-incidents'
    filters['data-count'] = props.get('count', '0')
    filters['data-search'] = props.get('search', '')
    filters['data-dataset'] = dataset

    if dataset == 'TOTAL':
        tag_name = 'num_incidents'
    elif dataset == 'JOURNALISTS':
        tag_name = 'num_journalist_targets'
    elif dataset == 'INSTITUTIONS':
        tag_name = 'num_institution_targets'
    else:
        tag_name = ''

    tag = "{{% {tag_name} {args} %}}".format(
        tag_name=tag_name,
        args=' '.join(
            '{k}="{v}"'.format(k=k.replace('param_', ''), v=v) for k, v in props.items() if k.startswith('param_')
        )
    )

    return DOM.create_element('span', filters, tag)


@hooks.register('register_admin_urls')
def mailchimp_urls():
    return [
        path(
            'mailchimp_interests/',
            MailchimpInterestsView.as_view(),
            name='mailchimp_interests',
        )
    ]


class SearchStatEntityElementHandler(InlineEntityElementHandler):
    """
    Database HTML to Draft.js ContentState.
    Converts the span tag into a SearchStat entity, with the right data.
    """
    mutability = 'IMMUTABLE'

    def get_attribute_data(self, attrs):
        """
        Take values from the HTML element's attributes
        """
        return {
            k.replace('data-', '').replace('-', '_'): v for k, v in attrs.items()
        }
