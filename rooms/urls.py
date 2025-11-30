from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_room, name="create_room"),
    path("<str:room_id>/", views.room_view, name="room_view"),
]
