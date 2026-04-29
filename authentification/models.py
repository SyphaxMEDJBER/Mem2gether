"""Extension simple du modele User Django.

UserProfile ajoute le role fonctionnel utilise par l'application:
professeur pour piloter une room, et etudiant pour la rejoindre.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Profil applicatif associe a un utilisateur Django."""

    ROLE_STUDENT = "student"
    ROLE_TEACHER = "teacher"
    ROLE_CHOICES = (
        (ROLE_TEACHER, "Professeur"),
        (ROLE_STUDENT, "Étudiant"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)

    @property
    def is_teacher(self):
        """Raccourci lisible pour les controles d'autorisation."""
        return self.role == self.ROLE_TEACHER

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    """Cree automatiquement un profil quand un compte utilisateur est cree."""
    if created:
        UserProfile.objects.create(user=instance)
