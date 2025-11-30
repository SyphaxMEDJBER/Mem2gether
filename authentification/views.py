from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from .forms import SignUpForm


def signup_view(request):
    """Inscription d'un nouvel utilisateur."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()          # crée l'utilisateur
            login(request, user)        # connecte directement après inscription
            return redirect("home")     # renvoie vers la page d'accueil
    else:
        form = SignUpForm()

    return render(request, "authentification/signup.html", {"form": form})


def signin_view(request):
    """Connexion d'un utilisateur existant."""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, "authentification/signin.html", {"form": form})


def logout_view(request):
    """Déconnexion de l'utilisateur."""
    logout(request)
    return redirect("home")


@login_required
def profil_view(request):
    """Page de profil simple (affiche les infos de l'utilisateur connecté)."""
    return render(request, "authentification/profil.html")
