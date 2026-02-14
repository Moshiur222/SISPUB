from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def admin_active(context, *url_names):
    request = context.get('request')
    if request and request.resolver_match:
        if request.resolver_match.url_name in url_names:
            return 'active'
    return ''

@register.simple_tag(takes_context=True)
def admin_show(context, *url_names):
    request = context.get('request')
    if request and request.resolver_match:
        if request.resolver_match.url_name in url_names:
            return 'show'
    return ''
