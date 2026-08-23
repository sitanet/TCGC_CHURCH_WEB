"""
Global context processors for templates.
"""
from django.conf import settings
from datetime import datetime


def site_settings(request):
    """
    Injects global site settings, church name, current year,
    homepage config, and user role flags into all template contexts.
    """
    config = None
    home_config = None

    try:
        from apps.core.models import SiteConfiguration, HomepageConfig
        config = SiteConfiguration.load()
        home_config = HomepageConfig.load()
    except Exception:
        pass

    is_staff_user = False
    user_role = None
    if request.user.is_authenticated:
        is_staff_user = getattr(request.user, "is_staff_member", False)
        user_role = getattr(request.user, "role", None)

    # Pending inbox counts for staff badge indicators
    unread_messages_count = 0
    new_prayer_requests_count = 0
    if is_staff_user:
        try:
            from apps.website.models import ContactMessage, PrayerRequest
            unread_messages_count = ContactMessage.objects.filter(status="new").count()
            new_prayer_requests_count = PrayerRequest.objects.filter(status="new").count()
        except Exception:
            pass

    return {
        "SITE_CONFIG": config,
        "HOMEPAGE_CONFIG": home_config,
        "CHURCH_NAME": getattr(settings, "CHURCH_NAME", "The CityGate Church"),
        "CHURCH_TAGLINE": getattr(settings, "CHURCH_TAGLINE", ""),
        "CURRENT_YEAR": datetime.now().year,
        "DEBUG": settings.DEBUG,
        "IS_STAFF_USER": is_staff_user,
        "CURRENT_USER_ROLE": user_role,
        "UNREAD_MESSAGES_COUNT": unread_messages_count,
        "NEW_PRAYER_REQUESTS_COUNT": new_prayer_requests_count,
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
