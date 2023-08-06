from urllib import urlencode

from django import template
from django.utils.encoding import smart_str

register = template.Library()


@register.inclusion_tag('inclusion_tags/paginator.html', takes_context=True)
def paginator(context, adjacent_pages=2):
    """
    Renders a ``inclusion_tags/paginator.html`` template with additional
    pagination context. To be used in conjunction with the ``object_list`` generic
    view.

    Adds pagination context variables for use in displaying first, adjacent pages and
    last page links in addition to those created by the ``object_list`` generic
    view.

    Taken from http://www.djangosnippets.org/snippets/73/

    Syntax::

        {% paginator[ <NUMBER_OF_ADJACENT_PAGES] %}

    Examples::

        {% paginator %}
        {% paginator 5 %}
    """
    if not 'page' in context:
        # improper use of paginator tag, bail out
        return {}

    query_params = '?p='
    if 'request' in context:
        get = context['request'].GET
        query_params = '?%s&p=' % urlencode(dict((k, smart_str(v)) for (k, v) in get.iteritems() if k != 'p'))

    page = context['page']
    page_no = int(page.number)

    s = max(1, page_no - adjacent_pages - max(0, page_no + adjacent_pages -
        page.paginator.num_pages))
    page_numbers = range(s, min(page.paginator.num_pages, s + 2 * adjacent_pages) + 1)

    return {
        'query_params': query_params,
        'page': page,
        'results_per_page': page.paginator.per_page,
        'page_numbers': page_numbers,
        'show_first': 1 not in page_numbers,
        'show_last': page.paginator.num_pages not in page_numbers,
    }

