# rooms/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # récupère le room_id depuis l'URL
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"room_{self.room_id}"

        # rejoint le groupe de la room
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # quitte le groupe quand le socket se ferme
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")

        user = (
            self.scope["user"].username
            if self.scope["user"].is_authenticated
            else "Anonyme"
        )

        # envoie à TOUT le groupe (tous les clients de la room)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": user,
            }
        )

    async def chat_message(self, event):
        # renvoie vers le navigateur
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "user": event["user"],
        }))
