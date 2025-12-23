from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import Room, Message, Participant

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group = f"room_{self.room_id}"

        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        user = self.scope["user"]
        if user.is_authenticated:
            await sync_to_async(Participant.objects.get_or_create)(
                room_id=self.room_id, user=user
            )

            await self.channel_layer.group_send(
                self.group,
                {
                    "type": "participants_update"
                }
            )

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            await sync_to_async(Participant.objects.filter(
                room_id=self.room_id, user=user
            ).delete)()

            await self.channel_layer.group_send(
                self.group,
                {
                    "type": "participants_update"
                }
            )

        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg = data.get("message")
        user = self.scope["user"]

        if user.is_authenticated and msg:
            room = await sync_to_async(Room.objects.get)(room_id=self.room_id)
            await sync_to_async(Message.objects.create)(
                room=room, user=user, content=msg
            )

            await self.channel_layer.group_send(
                self.group,
                {
                    "type": "chat_message",
                    "user": user.username,
                    "message": msg
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def participants_update(self, event):
        participants = await sync_to_async(
            lambda: list(
                Participant.objects.filter(room_id=self.room_id)
                .select_related("user")
                .values_list("user__username", flat=True)
            )
        )()

        await self.send(text_data=json.dumps({
            "type": "participants",
            "participants": participants
        }))
