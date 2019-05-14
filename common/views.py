import os

from django.http import HttpResponse
from wagtail.admin import messages
from wagtail.documents.views.serve import serve as wagtail_serve
from django.views.generic.edit import FormView
from .forms import TagMergeForm
from incident.models import IncidentPage
from django.utils.translation import gettext_lazy as _
from django.utils.text import capfirst


GITINFO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gitinfo')


# Wrap the wagtail document serving view to serve docs as inline rather
# than attachments, so that people can easily view them in-browser
# instead of downloading them and then opening them separately.
def serve(*args, **kwargs):
    response = wagtail_serve(*args, **kwargs)
    if response.get('content-disposition', '')[:10] == 'attachment':
        response['content-disposition'] = 'inline' + response['content-disposition'][10:]

    return response


class MergeView(FormView):
    template_name = 'modeladmin/merge_form.html'
    model_admin = None

    def form_valid(self, form):
        models_to_merge = form.cleaned_data['models_to_merge']
        new_model = form.cleaned_data['title_for_merged_models']

        new_model, created = self.model_admin.model.objects.get_or_create(title=new_model)

        fields = [
            {
                'accessor': relationship.get_accessor_name(),
                'remote_field': relationship.remote_field.name
            } for relationship in self.model_admin.model._meta.related_objects
        ]
        for field in fields:
            pages = list(IncidentPage.objects.filter(
                **{'{}__in'.format(field['remote_field']): models_to_merge}
            ))
            getattr(new_model, field['accessor']).add(*pages)
        new_model.save()
        models_to_merge.exclude(id=new_model.id).delete()
        messages.success(
            self.request,
            _("{0} successfully merged").format(
                capfirst(self.model_admin.model._meta.verbose_name_plural)
            )
        )

        return super().form_valid(form)

    def get_success_url(self):
        return self.model_admin.url_helper.index_url


class TagMergeView(MergeView):
    form_class = TagMergeForm


def gitinfo_view(request):
    with open(GITINFO_PATH, 'r') as f:
        contents = f.read()
    return HttpResponse(contents, content_type='text/plain; charset=us-ascii')
