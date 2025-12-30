from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ReactionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group = f"reactions_{self.room_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        reaction = data["reaction"]
        user = (
            self.scope["user"].username
            if self.scope["user"].is_authenticated
            else "Anonyme"
        )
        

        await self.channel_layer.group_send(
            self.group,
            {
                "type": "show_reaction",
                "reaction": reaction,
                "user": user,
                
            }
        )

    async def show_reaction(self, event):
        await self.send(json.dumps({
            "reaction": event["reaction"],
            "user": event["user"],
        }))
