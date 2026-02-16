from django.urls import path

from .api_views import course_notes_api

urlpatterns = [
    path("notes/", course_notes_api, name="course_notes_api"),
]
