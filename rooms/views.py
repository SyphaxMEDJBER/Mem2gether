from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Room, Participant, ImageQueue
import secrets
import os


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
        return render(request, "rooms/join_room.html", {"error": "Room inexistante"})


@login_required
def room_view(request, room_id):
    room = Room.objects.get(room_id=room_id)
    Participant.objects.get_or_create(room=room, user=request.user)

    # ===== UPLOAD IMAGE =====
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        ext = os.path.splitext(image.name)[1]
        filename = f"{secrets.token_hex(8)}{ext}"
        path = f"uploads/{room_id}/{filename}"
        default_storage.save(path, ContentFile(image.read()))

        ImageQueue.objects.filter(room=room).update(is_displayed=False)

        last = ImageQueue.objects.filter(room=room).order_by("-position").first()
        pos = last.position + 1 if last else 1

        img = ImageQueue.objects.create(
            room=room,
            image_url=f"/media/{path}",
            position=pos,
            uploaded_by=request.user,
            is_displayed=True
        )

        # ✅ temps réel photos (canal séparé)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"photos_{room_id}",
            {"type": "new_photo", "url": img.image_url, "user": request.user.username}
        )

        return redirect("room_view", room_id=room_id)

    participants = room.participants.select_related("user")
    messages = room.messages.select_related("user")
    images = room.image_queue.order_by("position")

    # ✅ participants temps réel (comme avant)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"room_{room_id}",
        {"type": "participants_update", "participants": [p.user.username for p in participants]}
    )

    return render(request, "rooms/room.html", {
        "room": room,
        "participants": participants,
        "messages": messages,
        "images": images
    })


@login_required
def current_image(request, room_id):
    img = ImageQueue.objects.filter(room__room_id=room_id, is_displayed=True).first()
    if img:
        return JsonResponse({"url": img.image_url, "user": img.uploaded_by.username if img.uploaded_by else "Anonyme"})
    return JsonResponse({"url": None, "user": None})


@login_required
def leave_room(request, room_id):
    room = Room.objects.get(room_id=room_id)
    channel_layer = get_channel_layer()

    if request.user == room.creator:
        async_to_sync(channel_layer.group_send)(f"room_{room_id}", {"type": "room_closed"})
        room.delete()
        return redirect("home")

    Participant.objects.filter(room=room, user=request.user).delete()

    participants = room.participants.select_related("user")
    async_to_sync(channel_layer.group_send)(
        f"room_{room_id}",
        {"type": "participants_update", "participants": [p.user.username for p in participants]}
    )

    return redirect("home")
