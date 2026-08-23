"""
Global context processors for templates.
"""
from django.conf import settings
from datetime import datetime


def site_settings(request):
    """
    Injects global site settings, church name, current year,
    and user role flags into all template contexts.
    """
    try:
        from apps.core.models import SiteConfiguration
        config = SiteConfiguration.load()
    except Exception:
        config = None

    is_staff_user = False
    user_role = None
    if request.user.is_authenticated:
        is_staff_user = getattr(request.user, "is_staff_member", False)
        user_role = getattr(request.user, "role", None)

    return {
        "SITE_CONFIG": config,
        "CHURCH_NAME": getattr(settings, "CHURCH_NAME", "The CityGate Church"),
        "CHURCH_TAGLINE": getattr(settings, "CHURCH_TAGLINE", ""),
        "CURRENT_YEAR": datetime.now().year,
        "DEBUG": settings.DEBUG,
        "IS_STAFF_USER": is_staff_user,
        "CURRENT_USER_ROLE": user_role,
    }


def active_announcements(request):
    """
    Injects any active emergency or top banner announcements.
    """
    try:
        from apps.announcements.models import Announcement
        active_items = Announcement.objects.filter(
            is_active=True,
            show_banner=True
        ).order_by("-priority", "-created_at")[:2]
    except Exception:
        active_items = []

    return {
        "BANNER_ANNOUNCEMENTS": active_items,
    }
