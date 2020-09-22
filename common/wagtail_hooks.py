import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from django.conf.urls import url
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from draftjs_exporter.dom import DOM
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineEntityElementHandler
from wagtail.contrib.modeladmin.helpers import AdminURLHelper, ButtonHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from wagtail.core import hooks
from webpack_loader.utils import get_files

from .models import CommonTag
from .views import TagMergeView, deploy_info_view


class URLHelperWithMerge(AdminURLHelper):
    @cached_property
    def merge_url(self):
        return self.get_action_url('merge')

    def get_action_url_pattern(self, action):
        if action in ('create', 'choose_parent', 'index', 'merge'):
            return self._get_action_url_pattern(action)
        return self._get_object_specific_action_url_pattern(action)


class ButtonHelperWithMerge(ButtonHelper):
    merge_button_classnames = []

    def merge_button(self, classnames_add=None, classnames_exclude=None):
        if classnames_add is None:
            classnames_add = []
        if classnames_exclude is None:
            classnames_exclude = []
        classnames = self.add_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        return {
            'url': self.url_helper.merge_url,
            'label': _('Merge %s') % self.verbose_name,
            'classname': cn,
            'title': _('Merge %s') % self.verbose_name,
        }


class MergeAdmin(ModelAdmin):
    button_helper_class = ButtonHelperWithMerge
    url_helper_class = URLHelperWithMerge

    index_template_name = 'modeladmin/index_with_merge.html'

    def merge_view(self, request):
        """
        Instantiates a class-based view to provide 'merge' functionality for
        the assigned model, or redirect to Wagtail's create view if the
        assigned model extends 'Page'. The view class used can be overridden by
        changing the 'create_view_class' attribute.
        """
        kwargs = {'model_admin': self}
        view_class = self.merge_view_class
        return view_class.as_view(**kwargs)(request)

    def get_admin_urls_for_registration(self):
        urls = super().get_admin_urls_for_registration()
        return urls + (
            url(
                self.url_helper.get_action_url_pattern('merge'),
                self.merge_view,
                name=self.url_helper.get_action_url_name('merge')
            ),
        )

    class Meta:
        abstract = True


class CommonTagAdmin(MergeAdmin):
    model = CommonTag
    merge_view_class = TagMergeView
    menu_label = 'Tags'
    menu_icon = 'tag'
    menu_order = 500  # will put in 4th place (000 being 1st, 100 2nd)
    add_to_settings_menu = False  # or True to add your model to the Settings sub-menu
    exclude_from_explorer = False  # or True to exclude pages of this type from Wagtail's explorer view
    list_display = ('title', 'incident_count')
    search_fields = ('title',)
    inspect_view_enabled = True
    inspect_view_fields = ('title',)

    def incident_count(self, tag):
        return tag.incident_count

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.with_incident_count()


modeladmin_register(CommonTagAdmin)


@hooks.register('register_admin_urls')
def urlconf_time():
    return [
        url(r'^version/?$', deploy_info_view, name='deployinfo'),
    ]


@hooks.register('register_rich_text_features')
def register_num_incidents_feature(features):
    features.default_features.append('numincidents')

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
