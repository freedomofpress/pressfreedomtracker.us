from django.views.generic import TemplateView

from common.devdata import CategoryPageFactory
from common.models.pages import CategoryPage
from common.choices import CATEGORY_SYMBOL_CHOICES
from incident.models import IncidentPage
from blog.tests.factories import BlogPageFactory


class StyleguideView(TemplateView):
    template_name = 'styleguide/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create sample incident for the styleguide without touching
        # the database.
        inc = IncidentPage.objects.first()
        all_categories = []
        for category_value, category_name in CATEGORY_SYMBOL_CHOICES:
            all_categories.append(
                CategoryPageFactory.build(
                    page_symbol=category_value,
                    **{category_value: True}
                )
            )

        context['category'] = CategoryPage.objects.first()
        context['all_categories'] = all_categories
        context['category_symbols'] = CATEGORY_SYMBOL_CHOICES
        context['incident'] = inc

        blog_page = BlogPageFactory.build(with_image=True)
        context['blog_page'] = blog_page

        blog_pages = BlogPageFactory.build_batch(3, with_image=True)
        context['blog_pages'] = blog_pages

        return context
