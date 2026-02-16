from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.views.decorators.http import require_POST
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import CourseNote, ImageQueue, Participant, Room
import json
import secrets
import os
import re

def _extract_youtube_id(url: str) -> str:
    if not url:
        return ""
    url = url.strip()

    # youtu.be/<id>
    m = re.search(r"youtu\.be/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

    # watch?v=<id>
    m = re.search(r"[?&]v=([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

    # /embed/<id>
    m = re.search(r"/embed/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

    # raw id
    if re.fullmatch(r"[A-Za-z0-9_-]{6,}", url):
        return url

    return ""


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

    channel_layer = get_channel_layer()

    # ===== SET YOUTUBE (all participants) =====
    if request.method == "POST":
        youtube_url = request.POST.get("youtube_url", "").strip()

        changed = False

        if youtube_url:
            vid = _extract_youtube_id(youtube_url)
            if vid and room.youtube_video_id != vid:
                room.youtube_video_id = vid
                room.youtube_state = "paused"
                room.youtube_time = 0.0
                room.youtube_updated_at = timezone.now()
                changed = True
                # reset sync baseline
                async_to_sync(channel_layer.group_send)(
                    f"youtube_{room_id}",
                    {"type": "youtube_event", "event": {"type": "set_video", "videoId": vid, "t": 0}}
                )

        if changed:
            room.save()

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

        async_to_sync(channel_layer.group_send)(
            f"photos_{room_id}",
            {
                "type": "new_photo",
                "id": img.id,
                "url": img.image_url,
                "position": img.position,
                "user": request.user.username
            }
        )

        return redirect("room_view", room_id=room_id)

    participants = room.participants.select_related("user")
    messages = room.messages.select_related("user")
    images = room.image_queue.order_by("position")

    # participants realtime
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
def set_mode(request, room_id):
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)

    room = Room.objects.get(room_id=room_id)
    Participant.objects.get_or_create(room=room, user=request.user)

    mode = request.POST.get("mode", "").strip()
    if mode not in ("photos", "youtube"):
        return JsonResponse({"error": "invalid_mode"}, status=400)

    if room.mode != mode:
        room.mode = mode
        room.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"room_{room_id}",
            {"type": "mode_update", "mode": mode}
        )

    return JsonResponse({"mode": room.mode})


@login_required
def current_image(request, room_id):
    img = ImageQueue.objects.filter(room__room_id=room_id, is_displayed=True).first()
    if img:
        return JsonResponse({"url": img.image_url, "user": img.uploaded_by.username if img.uploaded_by else "Anonyme"})
    return JsonResponse({"url": None, "user": None})


@login_required
def set_image(request, room_id):
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)

    image_id = request.POST.get("image_id")
    if not image_id:
        return JsonResponse({"error": "missing_image_id"}, status=400)

    try:
        img = ImageQueue.objects.select_related("room", "uploaded_by").get(id=image_id, room__room_id=room_id)
    except ImageQueue.DoesNotExist:
        return JsonResponse({"error": "image_not_found"}, status=404)

    ImageQueue.objects.filter(room=img.room).update(is_displayed=False)
    img.is_displayed = True
    img.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"photos_{room_id}",
        {"type": "new_photo", "url": img.image_url, "user": img.uploaded_by.username if img.uploaded_by else "Anonyme"}
    )

    return JsonResponse({"ok": True})


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


@login_required
@require_POST
def add_course_note(request, room_id):
    try:
        room = Room.objects.get(room_id=room_id)
    except Room.DoesNotExist:
        return JsonResponse({"ok": False, "error": "room_not_found"}, status=404)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)

    content = str(payload.get("content", "")).strip()
    if not content:
        return JsonResponse({"ok": False, "error": "missing_content"}, status=400)

    try:
        timecode = int(float(payload.get("timecode", 0)))
        if timecode < 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({"ok": False, "error": "invalid_timecode"}, status=400)

    note = CourseNote.objects.create(
        user=request.user,
        room=room,
        content=content,
        timecode=timecode,
    )
    return JsonResponse({"ok": True, "note_id": note.id, "timecode": note.timecode})
