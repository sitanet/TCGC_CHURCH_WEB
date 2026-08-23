"""
Telemetry recording API views.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .models import PageHit, MediaPlayEvent, DownloadEvent


class RecordMediaPlayApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        title = request.data.get("title", "Untitled")
        content_type = request.data.get("type", "sermon")
        content_id = int(request.data.get("id", 0))
        
        MediaPlayEvent.objects.create(
            content_title=title,
            content_type=content_type,
            content_id=content_id
        )
        return Response({"status": "recorded"})


class RecordDownloadApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        title = request.data.get("title", "Untitled")
        resource_type = request.data.get("type", "publication")
        resource_id = int(request.data.get("id", 0))

        DownloadEvent.objects.create(
            resource_title=title,
            resource_type=resource_type,
            resource_id=resource_id
        )
        return Response({"status": "recorded"})
