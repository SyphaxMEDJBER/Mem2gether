from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from authentification.models import UserProfile
from rooms.models import Room


class TeacherRolePermissionsTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher", password="secret123")
        self.teacher.userprofile.role = UserProfile.ROLE_TEACHER
        self.teacher.userprofile.save(update_fields=["role"])

        self.student = User.objects.create_user(username="student", password="secret123")
        self.student.userprofile.role = UserProfile.ROLE_STUDENT
        self.student.userprofile.save(update_fields=["role"])

        self.room = Room.objects.create(room_id="abcd1234", creator=self.teacher, mode="youtube")

    def test_student_cannot_create_room(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("create_room"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Seul un professeur peut creer une room.")

    def test_teacher_can_create_room(self):
        self.client.force_login(self.teacher)

        response = self.client.get(reverse("create_room"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Room.objects.filter(creator=self.teacher).count(), 2)
