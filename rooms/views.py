from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Participant
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import secrets

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt

import json

from .models import Room, Participant, Reaction


# ---------------------------------------------------------
# 1) CRÉER UNE ROOM
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# 4) AFFICHAGE D’UNE ROOM  (+ participants + réactions)
# ---------------------------------------------------------
@login_required
def room_view(request, room_id):
    # récupère la room ou 404 si n'existe pas
    room = get_object_or_404(Room, room_id=room_id)

    # ajoute l'utilisateur aux participants
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

    # compte les réactions pour cette room
    qs = (
        Reaction.objects.filter(room=room)
        .values("type")
        .annotate(c=Count("id"))
    )
    reaction_counts = {row["type"]: row["c"] for row in qs}
    for key in ["like", "fun", "wow", "love"]:
        reaction_counts.setdefault(key, 0)

    return render(request, "rooms/room.html", {
        "room": room,
        "participants": participants,
        "reaction_counts": reaction_counts,
    })


# ---------------------------------------------------------
# 5) API AJAX pour ajouter / enlever une réaction
# ---------------------------------------------------------
@csrf_exempt          # on désactive CSRF pour cette vue, plus simple pour l’AJAX
@require_POST
@login_required
def add_reaction(request, room_id):
    """
    Ajoute (ou supprime) une réaction pour l'utilisateur dans une room,
    puis renvoie les compteurs de toutes les réactions.
    """
    room = get_object_or_404(Room, room_id=room_id)
    ...


    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid json"}, status=400)

    reaction_type = data.get("type")
    if reaction_type not in ["like", "fun", "wow", "love"]:
        return JsonResponse({"error": "invalid type"}, status=400)

    # on crée ou on supprime (toggle)
    obj, created = Reaction.objects.get_or_create(
        room=room,
        user=request.user,
        type=reaction_type,
    )
    if not created:
        obj.delete()

    # recompter toutes les réactions pour cette room
    qs = (
        Reaction.objects.filter(room=room)
        .values("type")
        .annotate(c=Count("id"))
    )
    counts = {row["type"]: row["c"] for row in qs}
    for key in ["like", "fun", "wow", "love"]:
        counts.setdefault(key, 0)

    return JsonResponse({"counts": counts})
