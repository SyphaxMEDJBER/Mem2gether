from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room
import secrets

@login_required
def create_room(request):
    room_id = secrets.token_hex(4)

    Room.objects.create(
        room_id=room_id,
        creator=request.user
    )

    return redirect("room_view", room_id=room_id)

@login_required
def room_view(request, room_id):
    room = Room.objects.get(room_id=room_id)
    return render(request, "rooms/room.html", {"room": room})
