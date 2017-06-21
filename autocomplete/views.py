from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST


def render_page(page):
    page = page.specific
    if callable(getattr(page, 'autocomplete_label', None)):
        label = page.autocomplete_label()
    else:
        label = page.title
    return dict(id=page.id, label=label)


@require_GET
@login_required
def search(request):
    search_query = request.GET.get('query', '')
    page_type = request.GET.get('type', 'wagtailcore.Page')
    try:
        model = apps.get_model(page_type)
    except:
        return HttpResponseBadRequest

    queryset = model.objects.filter(title__icontains=search_query).live()

    exclude = request.GET.get('exclude', '')
    try:
        exclusions = [int(item) for item in exclude.split(',')]
        queryset = queryset.exclude(pk__in=exclusions)
    except:
        pass

    results = map(render_page, queryset[:20])
    return JsonResponse(dict(pages=list(results)))


@require_POST
@login_required
def create(request, *args, **kwargs):
    value = request.POST.get('value', None)
    if not value:
        return HttpResponseBadRequest

    page_type = request.POST.get('type', 'wagtailcore.Page')
    try:
        model = apps.get_model(page_type)
    except:
        return HttpResponseBadRequest

    method = getattr(model, 'autocomplete_create', None)
    if not callable(method):
        return HttpResponseBadRequest

    instance = method(value)
    return JsonResponse(render_page(instance))
