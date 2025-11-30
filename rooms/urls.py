from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_room, name="create_room"),
    path("join/", views.join_room_page, name="join_room_page"),
    path("join/submit/", views.join_room, name="join_room"),
    path("<str:room_id>/", views.room_view, name="room_view"),
]
