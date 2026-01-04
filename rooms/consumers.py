from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import Room, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group = f"chat_{self.room_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.channel_layer.group_add(f"room_{self.room_id}", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group, self.channel_name)
        await self.channel_layer.group_discard(f"room_{self.room_id}", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg = (data.get("message") or "").strip()
        if not msg:
            return

        user = self.scope["user"]

        if user.is_authenticated:
            room = await sync_to_async(Room.objects.get)(room_id=self.room_id)
            await sync_to_async(Message.objects.create)(room=room, user=user, content=msg)

        await self.channel_layer.group_send(
            self.group,
            {
                "type": "chat_message",
                "user": user.username if user.is_authenticated else "Anonyme",
                "message": msg,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "user": event["user"],
            "message": event["message"],
        }))

    async def participants_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "participants",
            "participants": event.get("participants", []),
        }))

    async def room_closed(self, event):
        await self.send(text_data=json.dumps({"type": "room_closed"}))

    async def mode_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "mode",
            "mode": event.get("mode"),
        }))


class PhotoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group = f"photos_{self.room_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def new_photo(self, event):
        await self.send(text_data=json.dumps({
            "type": "photo",
            "url": event.get("url"),
            "user": event.get("user", "Anonyme"),
        }))


class YouTubeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group = f"youtube_{self.room_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group,
            {"type": "youtube_event", "event": data}
        )

    async def youtube_event(self, event):
        await self.send(text_data=json.dumps(event["event"]))
