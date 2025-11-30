from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from .forms import SignUpForm


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()

    return render(request, "authentification/signup.html", {"form": form})


def signin_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            return redirect("home")

        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
            
    else:
        form = AuthenticationForm()

    return render(request, "authentification/signin.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def profil_view(request):
    return render(request, "authentification/profil.html")
