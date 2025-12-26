from channels.generic.websocket import AsyncWebsocketConsumer
import json

class PhotoConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"photos_{self.room_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def new_photo(self, event):
        await self.send(text_data=json.dumps({
            "type": "photo",
            "url": event["url"],
            "user": event["user"]
        }))
