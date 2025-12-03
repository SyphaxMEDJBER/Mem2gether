from .models import Room, Participant
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room
import secrets

# ---------------------------------------------------------
# 1) CRÉER UNE ROOM
# ---------------------------------------------------------
@login_required
def create_room(request):
    room_id = secrets.token_hex(4)

    Room.objects.create(
        room_id=room_id,
        creator=request.user
    )

    return redirect("room_view", room_id=room_id)


# ---------------------------------------------------------
# 2) PAGE POUR RENSEIGNER LE CODE D’UNE ROOM  (GET)
# ---------------------------------------------------------
@login_required
def join_room_page(request):
    return render(request, "rooms/join_room.html")


# ---------------------------------------------------------
# 3) TRAITEMENT DU FORMULAIRE POUR REJOINDRE (POST)
# ---------------------------------------------------------
@login_required
def join_room(request):
    if request.method == "POST":
        room_id = request.POST.get("room_id")

        try:
            Room.objects.get(room_id=room_id)
            return redirect("room_view", room_id=room_id)

        except Room.DoesNotExist:
            return render(request, "rooms/join_room.html", {
                "error": "Cette room n'existe pas."
            })

    return redirect("join_room_page")


# ---------------------------------------------------------
# 4) AFFICHAGE D’UNE ROOM
# ---------------------------------------------------------
@login_required
def room_view(request, room_id):
    room = Room.objects.get(room_id=room_id)
    return render(request, "rooms/room.html", {"room": room})








@login_required
def room_view(request, room_id):
    room = Room.objects.get(room_id=room_id)

    # Ajouter l’utilisateur aux participants si pas déjà dedans
    Participant.objects.get_or_create(room=room, user=request.user)

    participants = room.participants.select_related("user")

    return render(request, "rooms/room.html", {
        "room": room,
        "participants": participants
    })
