"""
Custom template tags and filters for The CityGate Church.
"""
from django import template
from django.utils.safestring import mark_safe
import math

register = template.Library()


@register.filter(name="format_bytes")
def format_bytes(bytes_value):
    """
    Format a byte count into a human-readable size (KB, MB, GB).
    """
    try:
        bytes_val = float(bytes_value)
    except (ValueError, TypeError):
        return "0 B"

    if bytes_val <= 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(bytes_val, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_val / p, 2)
    return f"{s} {units[i]}"


@register.simple_tag(takes_context=True)
def is_active_route(context, route_name, active_class="active"):
    """
    Returns an active CSS class if the current request path matches the route name.
    """
    request = context.get("request")
    if not request:
        return ""
    try:
        from django.urls import resolve
        current_url_name = resolve(request.path_info).url_name
        if current_url_name == route_name:
            return active_class
    except Exception:
        pass
    return ""
