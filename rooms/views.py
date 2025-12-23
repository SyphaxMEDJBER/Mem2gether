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
def join_room_page(request):
    return render(request, "rooms/join_room.html")


@login_required
def join_room(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")

        try:
            Room.objects.get(room_id=room_id)
            return redirect("room_view", room_id=room_id)
        except Room.DoesNotExist:
            return render(request, "rooms/join_room.html", {"error": "Cette room n'existe pas."})

    return redirect("join_room_page")


@login_required
def room_view(request, room_id):
    room = Room.objects.get(room_id=room_id)

    Participant.objects.get_or_create(room=room, user=request.user)

    participants = room.participants.select_related("user")
    messages = room.messages.select_related("user")

    layer = get_channel_layer()

    async_to_sync(layer.group_send)(
        f"participants_{room_id}",
        {
            "type": "send_update",
            "data": {
                "event": "update",
                "participants": [p.user.username for p in participants]
            }
        }
    )

    return render(request, "rooms/room.html", {
        "room": room,
        "participants": participants,
        "messages": messages,
    })


@login_required
def leave_room(request, room_id):
    room = Room.objects.get(room_id=room_id)
    layer = get_channel_layer()

    if room.creator == request.user:
        room.delete()

        async_to_sync(layer.group_send)(
            f"participants_{room_id}",
            {"type": "send_update", "data": {"event": "room_closed"}}
        )

        return redirect("home")

    Participant.objects.filter(room=room, user=request.user).delete()
    remaining = room.participants.all()

    async_to_sync(layer.group_send)(
        f"participants_{room_id}",
        {
            "type": "send_update",
            "data": {
                "event": "update",
                "participants": [p.user.username for p in remaining]
            }
        }
    )

    return redirect("home")
