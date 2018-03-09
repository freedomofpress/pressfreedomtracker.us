from wagtail.wagtaildocs.views.serve import serve as wagtail_serve
from django.views.generic.edit import FormView
from .forms import TagMergeForm
from incident.models import IncidentPage


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

        new_model, _ = self.model_admin.model.objects.get_or_create(title=new_model)

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
        models_to_merge.delete()

        return super().form_valid(form)

    def get_success_url(self):
        return self.model_admin.url_helper.index_url


class TagMergeView(MergeView):
    form_class = TagMergeForm
