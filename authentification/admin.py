"""Configuration de l'administration des profils utilisateurs."""

from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Permet de filtrer et rechercher les utilisateurs par role."""

    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")
