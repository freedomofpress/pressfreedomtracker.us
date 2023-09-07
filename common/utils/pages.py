from wagtail.core.models import Site


def get_page_for_request(request):
    """Look up the page instance that is being requested by a Request object

    Returns ``None`` if the page is not found, the ``Page`` instance otherwise.
    """
    site = Site.find_for_request(request)
    if site:
        path = request.path
        path_components = [component for component in path.split("/") if component]
        page, args, kwargs = site.root_page.specific.route(request, path_components)
        return page

    return None
