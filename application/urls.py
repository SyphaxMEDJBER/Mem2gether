from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Page d'accueil
    path(
        "",
        TemplateView.as_view(template_name="accueil/index.html"),
        name="home",
    ),

    # Page CGU
    path(
        "cgu/",
        TemplateView.as_view(template_name="accueil/cgu.html"),
        name="cgu",
    ),

    # Pour que /signup et /signin fonctionnent (et redirigent vers les vraies vues)
    path(
        "signup/",
        RedirectView.as_view(pattern_name="signup", permanent=False),
    ),
    path(
        "signin/",
        RedirectView.as_view(pattern_name="signin", permanent=False),
    ),

    # URLs d'authentification sous /auth/...
    path("auth/", include("authentification.urls")),



    path("rooms/", include("rooms.urls")),


    
]
