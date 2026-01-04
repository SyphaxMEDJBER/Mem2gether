from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_room, name="create_room"),
    path("join/", views.join_room, name="join_room"),
    path("<str:room_id>/", views.room_view, name="room_view"),
    path("<str:room_id>/set-mode/", views.set_mode, name="set_mode"),
    path("<str:room_id>/leave/", views.leave_room, name="leave_room"),

    path("<str:room_id>/current-image/", views.current_image, name="current_image"),
]
