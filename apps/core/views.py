"""
Core views, API root, and HTTP error handlers.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.conf import settings
from django.shortcuts import render
import sys
import django


class HealthCheckApiView(APIView):
    """
    Service health check endpoint.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "status": "healthy",
            "version": "1.0.0",
            "service": "The CityGate Church Platform API",
            "environment": "development" if settings.DEBUG else "production",
            "python_version": sys.version.split()[0],
            "django_version": django.get_version(),
        })


class ApiRootView(APIView):
    """
    The CityGate Church REST API Root (/api/v1/).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "title": "The CityGate Church REST API",
            "version": "v1",
            "documentation": "/api/v1/",
            "endpoints": {
                "health": request.build_absolute_uri("/api/v1/health/"),
                "teachings": request.build_absolute_uri("/api/v1/teachings/sermons/"),
                "series": request.build_absolute_uri("/api/v1/teachings/series/"),
                "galleries": request.build_absolute_uri("/api/v1/media/galleries/"),
                "people": request.build_absolute_uri("/api/v1/people/"),
                "ministries": request.build_absolute_uri("/api/v1/ministries/"),
                "events": request.build_absolute_uri("/api/v1/events/"),
                "conferences": request.build_absolute_uri("/api/v1/conferences/"),
                "publications": request.build_absolute_uri("/api/v1/publications/"),
                "articles": request.build_absolute_uri("/api/v1/articles/"),
                "announcements": request.build_absolute_uri("/api/v1/announcements/"),
                "streaming_status": request.build_absolute_uri("/api/v1/streaming/status/"),
                "search": request.build_absolute_uri("/api/v1/search/query/?q="),
                "auth_user": request.build_absolute_uri("/api/v1/auth/user/"),
            }
        })


def bad_request_view(request, exception=None):
    return render(request, "errors/400.html", status=400)


def permission_denied_view(request, exception=None):
    return render(request, "errors/403.html", status=403)


def page_not_found_view(request, exception=None):
    return render(request, "errors/404.html", status=404)


def server_error_view(request):
    return render(request, "errors/500.html", status=500)
