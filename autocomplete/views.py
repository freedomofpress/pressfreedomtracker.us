from django.apps import apps
from django.http import JsonResponse


def render_page(page):
    page = page.specific
    if callable(getattr(page, 'autocomplete_label', None)):
        label = page.autocomplete_label()
    else:
        label = page.title
    return dict(id=page.id, label=label)


def search(request):
    search_query = request.GET.get('query', '')
    type = request.GET.get('type', 'wagtailcore.Page')
    model = apps.get_model(type)
    queryset = model.objects.filter(title__icontains=search_query).live()[:20]
    results = map(render_page, queryset)
    return JsonResponse(dict(pages=list(results)))
