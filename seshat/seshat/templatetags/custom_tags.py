from django import template
from django.utils.http import urlencode

register = template.Library()


@register.filter
def active_application(application, url):
    '''
    Return whether the current url belongs to the application, ignoring
    the language prefix (e.g. /ar/stock/...)
    '''
    parts = [part for part in str(url).split('?')[0].split('/') if part]
    if parts and len(parts[0]) == 2 and parts[0].isalpha():
        parts = parts[1:]
    return bool(parts) and parts[0] == application


@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    '''
    Return the current query string updated with the given parameters,
    e.g. {% query_string page=2 %}
    '''
    request = context['request']
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value in (None, ''):
            params.pop(key, None)
        else:
            params[key] = value
    encoded = params.urlencode()
    return f'?{encoded}' if encoded else '?'


@register.filter
def percentage(value, total):
    '''
    Return value as a percentage of total (0 - 100)
    '''
    try:
        total = float(total)
        if total <= 0:
            return 0
        return max(0, min(100, round(float(value) / total * 100)))
    except (TypeError, ValueError):
        return 0


@register.simple_tag
def call_method(obj, method_name, *args):
    '''
    Call an object's method with arguments from a template
    '''
    return getattr(obj, method_name)(*args)


@register.filter
def initials(user):
    '''
    Return the initials of a user's full name (for avatars)
    '''
    first = (getattr(user, 'first_name', '') or '')[:1]
    last = (getattr(user, 'last_name', '') or '')[:1]
    return (first + last).upper() or str(user)[:1].upper()


@register.filter
def to_query(params):
    '''
    Encode a dict as a query string
    '''
    return urlencode(params or {})
