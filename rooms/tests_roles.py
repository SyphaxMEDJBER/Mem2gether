from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from authentification.models import UserProfile
from rooms.models import ImageQueue, Room


class TeacherRolePermissionsTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher", password="secret123")
        self.teacher.userprofile.role = UserProfile.ROLE_TEACHER
        self.teacher.userprofile.save(update_fields=["role"])

        self.student = User.objects.create_user(username="student", password="secret123")
        self.student.userprofile.role = UserProfile.ROLE_STUDENT
        self.student.userprofile.save(update_fields=["role"])

        self.room = Room.objects.create(room_id="abcd1234", creator=self.teacher)
        self.image = ImageQueue.objects.create(
            room=self.room,
            image_url="/media/uploads/test.png",
            position=1,
            is_displayed=True,
            uploaded_by=self.teacher,
        )

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

    def test_student_cannot_change_room_mode(self):
        self.client.force_login(self.student)

        response = self.client.post(reverse("set_mode", args=[self.room.room_id]), data={"mode": "youtube"})

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {"error": "teacher_only"})

    def test_student_cannot_select_image(self):
        self.client.force_login(self.student)

        response = self.client.post(
            reverse("set_image", args=[self.room.room_id]),
            data={"image_id": self.image.id},
        )

        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {"error": "teacher_only"})
