from channels.generic.websocket import AsyncWebsocketConsumer
import json

class RoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"room_{self.room_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "user": self.scope["user"].username,
                "message": data["message"]
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
        await self.send(text_data=json.dumps({
            "type": "room_closed"
        }))
