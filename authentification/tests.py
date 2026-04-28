from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserProfile


class SignupRoleTests(TestCase):
    def test_signup_saves_student_role(self):
        response = self.client.post(reverse("signup"), data={
            "username": "student1",
            "email": "student@example.com",
            "password1": "secret12345",
            "password2": "secret12345",
            "role": UserProfile.ROLE_STUDENT,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("home"))
        user = User.objects.get(username="student1")
        self.assertEqual(user.userprofile.role, UserProfile.ROLE_STUDENT)

    def test_signup_saves_teacher_role(self):
        response = self.client.post(reverse("signup"), data={
            "username": "prof1",
            "email": "prof@example.com",
            "password1": "secret12345",
            "password2": "secret12345",
            "role": UserProfile.ROLE_TEACHER,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("home"))
        user = User.objects.get(username="prof1")
        self.assertEqual(user.userprofile.role, UserProfile.ROLE_TEACHER)

    def test_signup_requires_role(self):
        response = self.client.post(reverse("signup"), data={
            "username": "user1",
            "email": "user@example.com",
            "password1": "secret12345",
            "password2": "secret12345",
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("signup"))
        self.assertFalse(User.objects.filter(username="user1").exists())
