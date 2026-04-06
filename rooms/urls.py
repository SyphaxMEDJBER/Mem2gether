from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_room, name="create_room"),
    path("join/", views.join_room, name="join_room"),
    path("<str:room_id>/", views.room_view, name="room_view"),
    path("<str:room_id>/sync-state/", views.youtube_sync_state, name="youtube_sync_state"),
    path("<str:room_id>/whiteboard-state/", views.whiteboard_sync_state, name="whiteboard_sync_state"),
    path("<str:room_id>/messages-state/", views.room_messages_state, name="room_messages_state"),
    path("<str:room_id>/add-note/", views.add_course_note, name="add_course_note"),
    path("<str:room_id>/leave/", views.leave_room, name="leave_room"),
    path("<str:room_id>/participants/", views.participants_json, name="participants_json"),
]
