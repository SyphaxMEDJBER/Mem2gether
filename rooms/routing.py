from django.urls import re_path
from .consumers import ChatConsumer, PhotoConsumer, YouTubeConsumer

websocket_urlpatterns = [
    re_path(r"ws/rooms/(?P<room_id>[0-9a-f]+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/photos/(?P<room_id>[0-9a-f]+)/$", PhotoConsumer.as_asgi()),
    re_path(r"ws/youtube/(?P<room_id>[0-9a-f]+)/$", YouTubeConsumer.as_asgi()),
]
