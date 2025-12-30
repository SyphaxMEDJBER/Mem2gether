from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout



def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

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
        user.save()

        login(request, user)
        return redirect("home")

    return render(request, "authentification/signup.html")


def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Identifiants invalides.")
            return redirect("signin")

        login(request, user)
        return redirect("home")

    return render(request, "authentification/signin.html")


def signout(request):
    logout(request)
    return redirect("home")






@login_required
def profil_view(request):
    return render(request, "authentification/profil.html")
        
def signout(request):
    logout(request)
    return redirect("home")
    
@login_required
def supprimer_compte(request):
    if request.method == "POST":
        request.user.delete()
        logout(request)
        return redirect("home")


