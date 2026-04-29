"""Formulaires de l'application d'authentification."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    """Formulaire Django standard enrichi avec l'email obligatoire."""

    email = forms.EmailField(required=True, label="Adresse e-mail")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
