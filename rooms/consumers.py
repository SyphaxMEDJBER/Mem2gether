"""Consumers WebSocket utilises par les rooms.

ChatConsumer diffuse les messages et les changements de participants.
YouTubeConsumer garde un canal temps reel pour les evenements video quand le
client utilise WebSocket. Les vues HTTP gardent aussi un etat persistant pour
permettre le recalage et les fallbacks par polling.
"""

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from django.utils import timezone
import time
from .models import Room, Message, Participant
from .views import _serialize_participants


class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket de chat et de presence pour une room."""

    @sync_to_async
    def _sync_join_and_payload(self, user):
        """Inscrit l'utilisateur dans la room et renvoie la liste visible."""
        # On ajoute l'utilisateur a la liste des participants.
        room = Room.objects.get(room_id=self.room_id)
        if user.is_authenticated:
            Participant.objects.get_or_create(room=room, user=user)
        return _serialize_participants(room)

    async def connect(self):
        """Abonne le client aux groupes chat et room."""
        # Chaque room a son propre groupe WebSocket.
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group = f"chat_{self.room_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.channel_layer.group_add(f"room_{self.room_id}", self.channel_name)
        await self.accept()

        # On previent les autres clients que la liste a change.
        participants = await self._sync_join_and_payload(self.scope["user"])
        await self.channel_layer.group_send(
            f"room_{self.room_id}",
            {
                "type": "participants_update",
                "participants": participants,
            }
        )

    async def disconnect(self, close_code):
        # On retire la connexion des groupes quand l'utilisateur part.
        await self.channel_layer.group_discard(self.group, self.channel_name)
        await self.channel_layer.group_discard(f"room_{self.room_id}", self.channel_name)

    async def receive(self, text_data):
        """Persiste puis diffuse un message de chat non vide."""
        # Le message recu vient du navigateur.
        data = json.loads(text_data)
        msg = (data.get("message") or "").strip()
        if not msg:
            return

        user = self.scope["user"]

        if user.is_authenticated:
            # On garde une copie du message en base.
            room = await sync_to_async(Room.objects.get)(room_id=self.room_id)
            await sync_to_async(Message.objects.create)(room=room, user=user, content=msg)

        # Puis on l'envoie a tous les clients de la room.
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


class YouTubeConsumer(AsyncWebsocketConsumer):
    """WebSocket de synchronisation du lecteur YouTube."""

    @sync_to_async
    def _can_control(self):
        """Seul le createur de la room peut piloter la video."""
        # Seul le createur de la room peut envoyer play/pause/seek.
        user = self.scope["user"]
        if not user.is_authenticated:
            return False
        room = Room.objects.select_related("creator").get(room_id=self.room_id)
        return room.creator_id == user.id

    async def _build_sync_event(self, room):
        """Construit l'etat video courant en tenant compte du temps ecoule."""
        # Si la video joue, on avance le temps avec l'horloge serveur.
        t = room.youtube_time or 0.0
        if room.youtube_state == "playing" and room.youtube_updated_at:
            delta = (timezone.now() - room.youtube_updated_at).total_seconds()
            t = max(0.0, t + delta)
        return {
            "type": "init",
            "videoId": room.youtube_video_id or "",
            "t": t,
            "state": room.youtube_state or "paused",
            "server_ts_ms": int(time.time() * 1000),
        }

    async def connect(self):
        # L'utilisateur rejoint le groupe video de sa room.
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group = f"youtube_{self.room_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        # On lui envoie tout de suite l'etat actuel de la video.
        room = await sync_to_async(Room.objects.get)(room_id=self.room_id)
        event = await self._build_sync_event(room)
        await self.send(text_data=json.dumps(event))

    async def disconnect(self, code):
        # On quitte le groupe video a la fermeture du WebSocket.
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        """Enregistre les commandes professeur puis les diffuse aux clients."""
        # Le navigateur envoie un evenement video.
        data = json.loads(text_data)
        event_type = data.get("type")

        if event_type == "sync_request":
            # Un client demande juste l'etat actuel.
            room = await sync_to_async(Room.objects.get)(room_id=self.room_id)
            event = await self._build_sync_event(room)
            await self.send(text_data=json.dumps(event))
            return

        # Les commandes video sont refusees si ce n'est pas le professeur.
        if not await self._can_control():
            return

        room = await sync_to_async(Room.objects.get)(room_id=self.room_id)
        now = timezone.now()

        # On met a jour l'etat sauvegarde selon le type d'evenement.
        if event_type == "set_video":
            video_id = data.get("videoId") or ""
            if video_id:
                room.youtube_video_id = video_id
            room.youtube_state = "paused"
            room.youtube_time = float(data.get("t", 0) or 0)
            room.youtube_updated_at = now

        if event_type == "play":
            room.youtube_state = "playing"
            room.youtube_time = float(data.get("t", 0) or 0)
            room.youtube_updated_at = now

        if event_type == "pause":
            room.youtube_state = "paused"
            room.youtube_time = float(data.get("t", 0) or 0)
            room.youtube_updated_at = now

        if event_type == "seek":
            room.youtube_time = float(data.get("t", 0) or 0)
            room.youtube_updated_at = now

        if event_type == "sync":
            state = data.get("state")
            if state in ("playing", "paused"):
                room.youtube_state = state
            if "t" in data and data.get("t") is not None:
                room.youtube_time = float(data.get("t") or 0)
            room.youtube_updated_at = now

        if event_type == "heartbeat":
            room.youtube_state = "playing"
            room.youtube_time = float(data.get("t", 0) or 0)
            room.youtube_updated_at = now

        # L'etat est sauvegarde pour les prochains utilisateurs.
        await sync_to_async(room.save)()

        # Puis il est diffuse aux clients connectes.
        outbound_event = {
            "type": event_type,
            "videoId": room.youtube_video_id or data.get("videoId") or "",
            "t": room.youtube_time,
            "state": room.youtube_state,
            "server_ts_ms": int(time.time() * 1000),
        }
        await self.channel_layer.group_send(
            self.group,
            {"type": "youtube_event", "event": outbound_event}
        )

    async def youtube_event(self, event):
        await self.send(text_data=json.dumps(event["event"]))
