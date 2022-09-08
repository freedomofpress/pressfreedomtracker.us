import json
import os

import marshmallow
import structlog
import mailchimp_marketing
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormView
from django.views.decorators.cache import never_cache
from django.views.generic import View, TemplateView
from wagtail.admin import messages
from wagtail.documents.views.serve import serve as wagtail_serve
from wagtail.core.models import Site

from common.models import CommonTag
from emails.models import SubscriptionSchema
from incident.models import IncidentPage, TopicPage
from .forms import TagMergeForm
from .utils import subscribe_for_site, MailchimpError


VERSION_INFO_SHORT_PATH = os.environ.get(
    "DJANGO_SHORT_VERSION_FILE", "/deploy/version-short.txt"
)
VERSION_INFO_FULL_PATH = os.environ.get(
    "DJANGO_FULL_VERSION_FILE", "/deploy/version-full.txt"
)


logger = structlog.get_logger()


def read_version_info_file(p):
    """Read deployment info file that is written by the deployment system

    This file contains git info (recent commits, messages), python
    version, dependency versions, and anything else that would be
    useful for debugging the deployed site.

    """
    try:
        with open(p, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "<file not found at {}>".format(p)


# Wrap the wagtail document serving view to serve docs as inline rather
# than attachments, so that people can easily view them in-browser
# instead of downloading them and then opening them separately.
def serve(*args, **kwargs):
    response = wagtail_serve(*args, **kwargs)
    if response.get('content-disposition', '')[:10] == 'attachment':
        response['content-disposition'] = 'inline' + response['content-disposition'][10:]

    return response


class SubscribeForSite(View):
    def post(self, request):
        if request.content_type == 'application/json':
            try:
                data = SubscriptionSchema().loads(request.body)
            except json.JSONDecodeError:
                logger.warning('JSON could not be decoded', json=request.body)
                return HttpResponse(status=400)
            except marshmallow.ValidationError as e:
                logger.warning('Invalid Mailchimp data received', error_message=str(e))
                return HttpResponse(status=400)
            try:
                site = Site.find_for_request(request)
                subscribe_for_site(site, data)
            except MailchimpError as err:
                logger.warning(
                    'Error communicating with Mailchimp',
                    mailchimp_error=getattr(err, 'text', str(err)),
                    mailchimp_status_code=getattr(err, 'status_code', '<none>'),
                )
                return JsonResponse(
                    {
                        'success': False,
                        'message': 'Error communicating with Mailchimp',
                    }
                )
            return JsonResponse({'success': True})
        elif request.content_type == 'application/x-www-form-urlencoded' or request.content_type == 'multipart/form-data':
            try:
                data = SubscriptionSchema().load(
                    request.POST,
                    unknown=marshmallow.EXCLUDE,
                )
            except marshmallow.ValidationError:
                return render(
                    request,
                    'common/_subscribe_error.html',
                    {'error_message': 'Invalid data submitted'}
                )
            try:
                site = Site.find_for_request(request)
                subscribe_for_site(site, data)
            except MailchimpError as err:
                logger.warning(
                    'Error communicating with Mailchimp',
                    mailchimp_error=getattr(err, 'text', str(err)),
                    mailchimp_status_code=getattr(err, 'status_code', '<none>'),
                )
                return render(
                    request,
                    'common/_subscribe_error.html',
                    {'error_message': 'An internal error occurred'}
                )
            return render(
                request,
                'common/_subscribe_thanks.html',
            )
        else:
            return HttpResponse(status=400)


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


class MailchimpInterestsView(TemplateView):
    template_name = 'wagtailadmin/mailchimp_interests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not getattr(settings, 'MAILCHIMP_API_KEY', None):
            context['error'] = 'Mailchimp API key not found'
            return context

        try:
            client = mailchimp_marketing.Client()
            client.set_config(
                {'api_key': settings.MAILCHIMP_API_KEY}
            )

            table_data = []
            response = client.lists.get_all_lists()
            for lst in response.get('lists', []):
                response = client.lists.get_list_interest_categories(lst['id'])

                for category in response.get('categories', []):
                    response = client.lists.list_interest_category_interests(
                        lst['id'],
                        category['id'],
                    )

                    for interest in response['interests']:
                        table_data.append(
                            (
                                lst.get('name'),
                                lst.get('id'),
                                category.get('title'),
                                interest.get('name'),
                                interest.get('id'),
                            )
                        )
        except mailchimp_marketing.api_client.ApiClientError as err:
            context['error'] = f'Error connecting to Mailchimp: {err.text}'
            return context

        context['table_data'] = table_data
        return context


def deploy_info_view(request):
    version_full_text = read_version_info_file(VERSION_INFO_FULL_PATH)
    return HttpResponse(version_full_text, content_type="text/plain")


@never_cache
def get_csrf_token(request):
    return HttpResponse(get_token(request), content_type='text/plain')


@never_cache
def health_ok(request):
    """Lightweight health-check with a 200 response code."""
    return HttpResponse("okay")


def health_version(request):
    """Also a health check, but returns the commit short-hash."""
    version_short_text = read_version_info_file(VERSION_INFO_SHORT_PATH)
    return HttpResponse(version_short_text, content_type="text/plain")
