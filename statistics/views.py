import inspect
import os

from django.shortcuts import render
from django.utils.safestring import mark_safe
from docutils.core import publish_parts


STATISTICS_DOCS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'STATISTICS.rst')


def introspect_func(name, f):
    return {
        'docstring': f.__doc__,
        'arguments': inspect.getargspec(f)[0],
        'name': name,
    }


# rendered_content/STATISTICS.rst must *not* contain dynamic user content.
def stats_guide_view(request):
    with open(STATISTICS_DOCS_PATH, 'r') as fp:
        parts = publish_parts(fp.read(), writer_name='html')
        rendered_content = parts['body']
    return render(request, 'statistics/statistics-guide.html', {
        'rendered_content': mark_safe(rendered_content)  # nosec
    })
