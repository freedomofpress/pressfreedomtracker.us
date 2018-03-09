from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register)
from wagtail.contrib.modeladmin.helpers import AdminURLHelper, ButtonHelper
from django.conf.urls import url
from django.utils.translation import ugettext as _
from django.utils.functional import cached_property
from .models import CommonTag
from .views import TagMergeView


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
    list_display = ('title',)
    search_fields = ('title',)


modeladmin_register(CommonTagAdmin)
