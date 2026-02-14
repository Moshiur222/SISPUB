from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def active(context, *url_names):
    request = context['request']
    if request.resolver_match:
        if request.resolver_match.url_name in url_names:
            return 'active'
    return ''