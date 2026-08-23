"""
Views and API for streaming.
"""
from rest_framework import views, response
from .models import LiveStreamChannel
from .serializers import LiveStreamChannelSerializer


class LiveStreamStatusApiView(views.APIView):
    """
    API endpoint returning current live stream broadcast status.
    """
    def get(self, request):
        channel = LiveStreamChannel.load()
        serializer = LiveStreamChannelSerializer(channel)
        return response.Response(serializer.data)
