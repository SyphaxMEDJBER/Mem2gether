from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Participant
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import secrets

@login_required
def create_room(request):
    room_id = secrets.token_hex(4)
    Room.objects.create(room_id=room_id, creator=request.user)
    return redirect("room_view", room_id=room_id)

@login_required
def join_room(request):
    if request.method == "GET":
        return render(request, "rooms/join_room.html")

    room_id = request.POST.get("room_id")

    try:
        Room.objects.get(room_id=room_id)
        return redirect("room_view", room_id=room_id)
    except Room.DoesNotExist:
        return render(request, "rooms/join_room.html", {
            "error": "Room inexistante"
        })

@login_required
def room_view(request, room_id):
    room = Room.objects.get(room_id=room_id)
    Participant.objects.get_or_create(room=room, user=request.user)

    participants = room.participants.select_related("user")
    messages = room.messages.select_related("user")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"room_{room_id}",
        {
            "type": "participants_update",
            "participants": [p.user.username for p in participants]
        }
    )

    return render(request, "rooms/room.html", {
        "room": room,
        "participants": participants,
        "messages": messages
    })

@login_required
def leave_room(request, room_id):
    room = Room.objects.get(room_id=room_id)
    channel_layer = get_channel_layer()

    if request.user == room.creator:
        async_to_sync(channel_layer.group_send)(
            f"room_{room_id}",
            {
                "type": "room_closed"
            }
        )
        room.delete()
        return redirect("home")

    Participant.objects.filter(room=room, user=request.user).delete()

    participants = room.participants.select_related("user")
    async_to_sync(channel_layer.group_send)(
        f"room_{room_id}",
        {
            "type": "participants_update",
            "participants": [p.user.username for p in participants]
        }
    )

    return redirect("home")
