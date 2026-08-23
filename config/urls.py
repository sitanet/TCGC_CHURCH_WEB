"""
The CityGate Church URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import HealthCheckApiView, ApiRootView
from apps.accounts.views import CurrentUserApiView

# API v1 URLs
api_v1_patterns = [
    path("", ApiRootView.as_view(), name="api_root"),
    path("health/", HealthCheckApiView.as_view(), name="api_health"),
    path("auth/user/", CurrentUserApiView.as_view(), name="api_current_user"),
    path("teachings/", include("apps.teachings.urls")),
    path("media/", include("apps.media_library.urls")),
    path("people/", include("apps.people.urls")),
    path("ministries/", include("apps.ministries.urls")),
    path("events/", include("apps.events.urls")),
    path("conferences/", include("apps.conferences.urls")),
    path("publications/", include("apps.publications.urls")),
    path("articles/", include("apps.articles.urls")),
    path("announcements/", include("apps.announcements.urls")),
    path("streaming/", include("apps.streaming.urls")),
    path("search/", include("apps.search.urls")),
    path("analytics/", include("apps.analytics.urls")),
]

urlpatterns = [
    # Fallback Django admin
    path("django-admin/", admin.site.urls),
    
    # Custom Administrative Dashboard (Staff / Admins)
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),
    
    # User Authentication & Profiles
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    
    # Django REST Framework API v1
    path("api/v1/", include((api_v1_patterns, "api_v1"))),
    
    # Public Website
    path("", include("apps.website.urls", namespace="website")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom Error Handlers
handler400 = "apps.core.views.bad_request_view"
handler403 = "apps.core.views.permission_denied_view"
handler404 = "apps.core.views.page_not_found_view"
handler500 = "apps.core.views.server_error_view"

