from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView

from django.conf import settings
from django.http import FileResponse, Http404
import os

def serve_media(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(file_path):
        raise Http404
    return FileResponse(open(file_path, "rb"))

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", TemplateView.as_view(template_name="accueil/index.html"), name="home"),
    path("cgu/", TemplateView.as_view(template_name="accueil/cgu.html"), name="cgu"),

    path("signup/", RedirectView.as_view(pattern_name="signup", permanent=False)),
    path("signin/", RedirectView.as_view(pattern_name="signin", permanent=False)),

    path("auth/", include("authentification.urls")),
    path("rooms/", include("rooms.urls")),

    # MEDIA (obligatoire si tu lances avec daphne)
    path("media/<path:path>", serve_media),
]
