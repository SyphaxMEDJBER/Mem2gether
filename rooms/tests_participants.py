from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async

from authentification.models import UserProfile
from rooms.models import Participant, Room
from application.asgi import application


class RoomLeaveBehaviorTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username="teacher", password="secret123")
        self.teacher.userprofile.role = UserProfile.ROLE_TEACHER
        self.teacher.userprofile.save(update_fields=["role"])

        self.student = User.objects.create_user(username="student", password="secret123")
        self.room = Room.objects.create(room_id="roomkeep1", creator=self.teacher)
        Participant.objects.create(room=self.room, user=self.teacher)
        Participant.objects.create(room=self.room, user=self.student)

    def test_teacher_leaving_does_not_delete_room(self):
        self.client.force_login(self.teacher)

        response = self.client.get(reverse("leave_room", args=[self.room.room_id]))

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(Room.objects.filter(room_id=self.room.room_id).exists())
        self.assertFalse(Participant.objects.filter(room=self.room, user=self.teacher).exists())
        self.assertTrue(Participant.objects.filter(room=self.room, user=self.student).exists())


class RoomParticipantsRealtimeTests(TestCase):
    async def test_joining_socket_broadcasts_updated_participants(self):
        teacher = await database_sync_to_async(User.objects.create_user)(
            username="teacher_rt",
            password="secret123",
        )
        await database_sync_to_async(UserProfile.objects.filter(user=teacher).update)(
            role=UserProfile.ROLE_TEACHER,
        )

        student = await database_sync_to_async(User.objects.create_user)(
            username="student_rt",
            password="secret123",
        )
        room = await database_sync_to_async(Room.objects.create)(
            room_id="feedbeef",
            creator=teacher,
        )
        await database_sync_to_async(Participant.objects.create)(room=room, user=teacher)

        teacher_ws = WebsocketCommunicator(application, f"/ws/rooms/{room.room_id}/")
        teacher_ws.scope["user"] = teacher
        connected, _ = await teacher_ws.connect()
        self.assertTrue(connected)
        await teacher_ws.receive_json_from()

        student_ws = WebsocketCommunicator(application, f"/ws/rooms/{room.room_id}/")
        student_ws.scope["user"] = student
        connected, _ = await student_ws.connect()
        self.assertTrue(connected)

        teacher_payload = await teacher_ws.receive_json_from()
        student_payload = await student_ws.receive_json_from()

        expected = {
            ("teacher_rt", True),
            ("student_rt", False),
        }

        self.assertEqual(teacher_payload["type"], "participants")
        self.assertEqual(student_payload["type"], "participants")
        self.assertEqual(
            {(item["username"], item["is_creator"]) for item in teacher_payload["participants"]},
            expected,
        )
        self.assertEqual(
            {(item["username"], item["is_creator"]) for item in student_payload["participants"]},
            expected,
        )

        await teacher_ws.disconnect()
        await student_ws.disconnect()
