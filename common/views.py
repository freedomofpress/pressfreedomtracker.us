import os

from django.http import HttpResponse
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView
from django.views.decorators.cache import never_cache
from wagtail.admin import messages
from wagtail.documents.views.serve import serve as wagtail_serve

from common.models import CommonTag
from incident.models import IncidentPage, TopicPage
from .forms import TagMergeForm


DEPLOYINFO_PATH = os.environ.get('DJANGO_VERSION_FILE', '/deploy/version')


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


class TagMergeView(FormView):
    form_class = TagMergeForm
    template_name = 'modeladmin/merge_form.html'
    model_admin = None

    def get_success_url(self):
        return self.model_admin.url_helper.index_url

    def form_valid(self, form):
        models_to_merge = form.cleaned_data['models_to_merge']
        new_tag_title = form.cleaned_data['title_for_merged_models']

        tag, _ = CommonTag.objects.get_or_create(title=new_tag_title)

        pages = IncidentPage.objects.filter(tags__in=models_to_merge)
        tag.tagged_items.add(*list(pages))
        TopicPage.objects.filter(
            incident_tag__in=models_to_merge
        ).update(incident_tag=tag)

        models_to_merge.exclude(pk=tag.pk).delete()
        return super().form_valid(form)


def deploy_info_view(request):
    try:
        with open(DEPLOYINFO_PATH, 'r') as f:
            contents = f.read()
    except FileNotFoundError:
        contents = "<file not found at {}>".format(DEPLOYINFO_PATH)
    return HttpResponse(contents, content_type='text/plain; charset=us-ascii')


@never_cache
def health_ok(request):
    """Lightweight health-check with a 200 response code."""
    return HttpResponse("okay")
