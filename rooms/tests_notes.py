import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from rooms.models import CourseNote, Room


class CourseNotesStorageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="secret123")
        self.room = Room.objects.create(room_id="room1234", creator=self.user)

    def test_note_is_saved_with_user_room_content_and_timecode(self):
        self.client.login(username="alice", password="secret123")

        response = self.client.post(
            reverse("course_notes_api"),
            data=json.dumps(
                {
                    "room_id": self.room.room_id,
                    "content": "Point important du cours",
                    "timecode": 42,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        note = CourseNote.objects.get()
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.room, self.room)
        self.assertEqual(note.content, "Point important du cours")
        self.assertEqual(note.timecode, 42)

    def test_get_notes_returns_notes_ordered_by_timecode(self):
        self.client.login(username="alice", password="secret123")

        CourseNote.objects.create(
            user=self.user,
            room=self.room,
            content="Deuxieme note",
            timecode=84,
        )
        CourseNote.objects.create(
            user=self.user,
            room=self.room,
            content="Premiere note",
            timecode=12,
        )

        response = self.client.get(
            reverse("course_notes_api"),
            data={"room_id": self.room.room_id},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["room_id"], self.room.room_id)
        self.assertEqual(len(payload["notes"]), 2)
        self.assertEqual(payload["notes"][0]["content"], "Premiere note")
        self.assertEqual(payload["notes"][0]["timecode"], 12)
        self.assertEqual(payload["notes"][1]["content"], "Deuxieme note")
        self.assertEqual(payload["notes"][1]["timecode"], 84)

    def test_notes_api_requires_authentication(self):
        response = self.client.get(
            reverse("course_notes_api"),
            data={"room_id": self.room.room_id},
        )

        self.assertEqual(response.status_code, 302)
