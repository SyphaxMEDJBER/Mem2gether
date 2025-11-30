from django.urls import path, include
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("signin/", views.signin_view, name="signin"),
    path("logout/", views.logout_view, name="logout"),
    path("profil/", views.profil_view, name="profil"),
    path("rooms/", include("rooms.urls")),

]
