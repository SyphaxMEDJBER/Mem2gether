"""Routes HTTP de l'API JSON."""

from django.urls import path

from .api_views import course_notes_api

# Routes de l'API utilisees par le JavaScript.
urlpatterns = [
    # Notes de cours: lecture et creation.
    path("notes/", course_notes_api, name="course_notes_api"),
]
