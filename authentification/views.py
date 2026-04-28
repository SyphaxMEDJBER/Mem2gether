from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile



def signup(request):
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""
        role = request.POST.get("role")

        if role not in {UserProfile.ROLE_TEACHER, UserProfile.ROLE_STUDENT}:
            messages.error(request, "Choisissez un rôle entre professeur et étudiant.")
            return redirect("signup")

        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Nom d'utilisateur déjà utilisé.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email déjà utilisé.")
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.save(update_fields=["role"])

        login(request, user)
        return redirect("home")

    return render(request, "authentification/signup.html")


def signin(request):
    if request.method == "POST":
        identifier = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        username = identifier
        if "@" in identifier:
            found_user = User.objects.filter(email__iexact=identifier).first()
            if found_user:
                username = found_user.username

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Identifiants invalides (nom d'utilisateur/email ou mot de passe).")
            return redirect("signin")

        login(request, user)
        messages.success(request, f"Bienvenue {user.username}.")
        return redirect("home")

    return render(request, "authentification/signin.html")


def signout(request):
    logout(request)
    return redirect("home")






@login_required
def profil_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "authentification/profil.html", {"profile": profile})
    
@login_required
def supprimer_compte(request):
    if request.method == "POST":
        request.user.delete()
        logout(request)
        return redirect("home")

