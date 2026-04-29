"""Consumer generique historique pour diffuser des evenements de room.

Le routage actuel utilise surtout ChatConsumer dans rooms.consumers, mais ce
consumer reste utile comme exemple simple de broadcast par groupe Channels.
"""

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class RoomConsumer(AsyncWebsocketConsumer):
    """Diffuse tout message recu a tous les clients de la meme room."""

    async def connect(self):
        # On recupere l'id de la room depuis l'URL WebSocket.
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"room_{self.room_id}"

        # On ajoute cette connexion au groupe de la room.
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Quand la connexion se ferme, on quitte le groupe.
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Tout message recu est renvoye a toute la room.
        data = json.loads(text_data)

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast",
                "data": data
            }
        )

    async def broadcast(self, event):
        # Envoi final vers le navigateur.
        await self.send(text_data=json.dumps(event["data"]))
