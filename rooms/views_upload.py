from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Room, ImageQueue
import secrets, os

@login_required
def upload_image_iframe(request, room_id):
    room = Room.objects.get(room_id=room_id)

    message = None

    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        ext = os.path.splitext(image.name)[1]
        filename = f"{secrets.token_hex(8)}{ext}"
        path = f"uploads/{room_id}/{filename}"

        default_storage.save(path, ContentFile(image.read()))

        last = ImageQueue.objects.filter(room=room).order_by("-position").first()
        pos = last.position + 1 if last else 1

        ImageQueue.objects.create(
            room=room,
            image_url=f"/media/{path}",
            position=pos,
            uploaded_by=request.user,
            is_displayed=(pos == 1)
        )

        message = "Image ajoutée"

    return render(request, "rooms/upload_iframe.html", {
        "room": room,
        "message": message
    })
