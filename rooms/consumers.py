from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import Room, Message

class RoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"room_{self.room_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @database_sync_to_async
    def save_message(self, room_id, user, content):
        try:
            room = Room.objects.get(room_id=room_id)
        except Room.DoesNotExist:
            return
        Message.objects.create(
            room=room,
            user=user if (user and user.is_authenticated) else None,
            content=content
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg = (data.get("message") or "").strip()
        if not msg:
            return

        user = self.scope["user"]
        username = user.username if (user and user.is_authenticated) else "Anonyme"

        # ✅ Sauvegarde DB (tu récupères l’historique)
        await self.save_message(self.room_id, user, msg)

        # ✅ Broadcast temps réel
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "user": username,
                "message": msg
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "user": event["user"],
            "message": event["message"]
        }))

    async def participants_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "participants",
            "participants": event["participants"]
        }))

    async def room_closed(self, event):
        await self.send(text_data=json.dumps({"type": "room_closed"}))
