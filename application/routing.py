from django.urls import re_path
from rooms.consumers import RoomConsumer
from rooms.consumers_photos import PhotoConsumer

websocket_urlpatterns = [
    re_path(r"ws/rooms/(?P<room_id>\w+)/$", RoomConsumer.as_asgi()),
    re_path(r"ws/photos/(?P<room_id>\w+)/$", PhotoConsumer.as_asgi()),
]
