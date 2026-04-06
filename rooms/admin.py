from django.contrib import admin
from .models import CourseNote, Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_id", "creator", "mode", "created_at")
    list_filter = ("mode", "created_at")
    search_fields = ("room_id", "creator__username")

@admin.register(CourseNote)
class CourseNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "room", "user", "timecode", "created_at")
    list_filter = ("created_at",)
    search_fields = ("room__room_id", "user__username", "content")
    ordering = ("room", "timecode", "created_at")
