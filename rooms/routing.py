"""Routes WebSocket Channels pour les rooms."""

from django.urls import re_path
from .consumers import ChatConsumer, YouTubeConsumer


websocket_urlpatterns = [
    re_path(r"ws/rooms/(?P<room_id>[0-9a-f]+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/youtube/(?P<room_id>[0-9a-f]+)/$", YouTubeConsumer.as_asgi()),
]
