from wagtail.wagtaildocs.views.serve import serve as wagtail_serve
from django.views.generic.edit import FormView
from .forms import TagMergeForm
from django.forms.utils import ErrorList
from incident.models import IncidentPage
from common.models import CommonTag


# Wrap the wagtail document serving view to serve docs as inline rather
# than attachments, so that people can easily view them in-browser
# instead of downloading them and then opening them separately.
def serve(*args, **kwargs):
    response = wagtail_serve(*args, **kwargs)
    if response.get('content-disposition', '')[:10] == 'attachment':
        response['content-disposition'] = 'inline' + response['content-disposition'][10:]

    return response

# Inherit from FormView - takes a model and a form
# Autocomplete field and new name field
# override process_form method
# wagtail styleguide for styles
class MergeView(FormView):
    template_name = 'modeladmin/merge_form.html'
    form_class = TagMergeForm
    model_admin = None

    def form_valid(self, form):
        # TODO write test that fails if CommonTag._meta.related_objects has multiple results
        tags = form.cleaned_data['tags']
        new_tag = form.cleaned_data['title_for_merged_tags']

        new_tag, _ = CommonTag.objects.get_or_create(title=new_tag)
        pages = list(IncidentPage.objects.filter(tags__in=tags))
        new_tag.tagged_items.add(*pages)
        new_tag.save()
        tags.delete()

        return super().form_valid(form)

    def get_success_url(self):
        return self.model_admin.url_helper.index_url
