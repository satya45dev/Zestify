# D:\Zestify\ecommerce\core\templatetags\custom_filters.py

from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Splits a string by the given argument. Usage: {{ value|split:" " }}"""
    return value.split(arg)

@register.filter
def status_badge_class(status):
    """Returns a Bootstrap class based on the order status."""
    status = status.lower()
    if 'delivered' in status:
        return 'bg-success text-white'
    elif 'shipped' in status or 'packed' in status:
        return 'bg-info text-dark'
    elif 'cancelled' in status:
        return 'bg-danger text-white'
    else:
        # Default for Processing, Pending, etc.
        return 'bg-warning text-dark'


