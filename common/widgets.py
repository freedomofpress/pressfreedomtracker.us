import json

from django.forms import Widget
from django.utils.html import format_html
from django.conf import settings

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore import hooks
from webpack_loader.utils import get_loader

from autocomplete.views import render_page


@hooks.register('insert_editor_js')
def editor_js():
    chunks = get_loader('DEFAULT').get_bundle('editor')
    chunk = next(filter(lambda chunk: chunk['name'].endswith('.js'), chunks))
    if not chunk:
        return ''
    html = '<script type="text/javascript" src="{}">'.format(chunk['url'])
    return format_html(html)


class Autocomplete(Widget):
    template_name = 'autocomplete.html'

    def format_value(self, value):
        if type(value) == list:
            return json.dumps([render_page(page) for page in Page.objects.filter(id__in=value)])
        return '[]'

    def value_from_datadict(self, data, files, name):
        return [obj['id'] for obj in json.loads(data.get(name))]
