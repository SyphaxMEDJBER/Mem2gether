"""Configuration de l'interface d'administration Django pour les rooms."""

from django.contrib import admin
from .models import CourseNote, Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    """Vue admin des sessions collaboratives."""

    # Colonnes affichees dans la liste des rooms.
    list_display = ("room_id", "creator", "mode", "created_at")

    # Filtres rapides dans l'interface admin.
    list_filter = ("mode", "created_at")

    # Champs utilisables dans la recherche admin.
    search_fields = ("room_id", "creator__username")

@admin.register(CourseNote)
class CourseNoteAdmin(admin.ModelAdmin):
    """Vue admin des notes horodatees."""

    # Colonnes affichees dans la liste des notes.
    list_display = ("id", "room", "user", "timecode", "created_at")

    # Filtre par date de creation.
    list_filter = ("created_at",)

    # Recherche par room, utilisateur ou contenu.
    search_fields = ("room__room_id", "user__username", "content")

    # Tri par room puis par moment de la video.
    ordering = ("room", "timecode", "created_at")
