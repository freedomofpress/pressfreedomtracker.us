from django.http import JsonResponse

from wagtail.wagtailcore.models import Page


def render_page(page):
    page = page.specific
    if callable(getattr(page, 'autocomplete_label', None)):
        label = page.autocomplete_label()
    else:
        label = page.title
    return dict(id=page.id, label=label)


def search(request):
    search_query = request.GET.get('query', '')
    results = map(
        render_page,
        Page.objects.filter(title__icontains=search_query)[:20],
    )
    return JsonResponse(dict(
        pages=list(results),
    ))
