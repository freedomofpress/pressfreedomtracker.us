from django import template
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _


register = template.Library()

@register.simple_tag(takes_context=True)
def page_table_header_label(context, label=None, parent_page_title=None, **kwargs):
    """
    Wraps table_header_label to add a title attribute based on the parent page title and the column label
    """
    if label:
        translation_context = {"parent": parent_page_title, "label": label}
        ascending_title_text = (
            _(
                "Sort the order of child pages within '%(parent)s' by '%(label)s' in ascending order."
            )
            % translation_context
        )
        descending_title_text = (
            _(
                "Sort the order of child pages within '%(parent)s' by '%(label)s' in descending order."
            )
            % translation_context
        )
    else:
        ascending_title_text = None
        descending_title_text = None

    return table_header_label(
        context,
        label=label,
        ascending_title_text=ascending_title_text,
        descending_title_text=descending_title_text,
        **kwargs,
    )


@register.simple_tag(takes_context=True)
def table_header_label(
    context,
    label=None,
    sortable=True,
    ordering=None,
    sort_context_var="ordering",
    sort_param="ordering",
    sort_field=None,
    ascending_title_text=None,
    descending_title_text=None,
):
    """
    A label to go in a table header cell, optionally with a 'sort' link that alternates between
    forward and reverse sorting
    label = label text
    ordering = current active ordering. If not specified, we will fetch it from the template context variable
        given by sort_context_var. (We don't fetch it from the URL because that wouldn't give the view method
        the opportunity to set a default)
    sort_param = URL parameter that indicates the current active ordering
    sort_field = the value for sort_param that indicates that sorting is currently on this column.
        For example, if sort_param='ordering' and sort_field='title', then a URL parameter of
        ordering=title indicates that the listing is ordered forwards on this column, and a URL parameter
        of ordering=-title indicated that the listing is ordered in reverse on this column
    ascending_title_text = title attribute to use on the link when the link action will sort in ascending order
    descending_title_text = title attribute to use on the link when the link action will sort in descending order
    To disable sorting on this column, set sortable=False or leave sort_field unspecified.
    """
    if not sortable or not sort_field:
        # render label without a sort link
        return label

    if ordering is None:
        ordering = context.get(sort_context_var)
    reverse_sort_field = "-%s" % sort_field

    if ordering == sort_field:
        # currently ordering forwards on this column; link should change to reverse ordering
        attrs = {
            "href": querystring(context, **{sort_param: reverse_sort_field}),
            "class": "icon icon-arrow-down-after teal",
        }
        if descending_title_text is not None:
            attrs["title"] = descending_title_text

    elif ordering == reverse_sort_field:
        # currently ordering backwards on this column; link should change to forward ordering
        attrs = {
            "href": querystring(context, **{sort_param: sort_field}),
            "class": "icon icon-arrow-up-after teal",
        }
        if ascending_title_text is not None:
            attrs["title"] = ascending_title_text

    else:
        # not currently ordering on this column; link should change to forward ordering
        attrs = {
            "href": querystring(context, **{sort_param: sort_field}),
            "class": "icon icon-arrow-down-after",
        }
        if ascending_title_text is not None:
            attrs["title"] = ascending_title_text

    attrs_string = format_html_join(" ", '{}="{}"', attrs.items())

    return format_html(
        # need whitespace around label for correct positioning of arrow icon
        "<a {attrs}> {label} </a>",
        attrs=attrs_string,
        label=label,
    )
