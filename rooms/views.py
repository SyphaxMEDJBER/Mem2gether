from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import CourseNote, Participant, Room
from authentification.models import UserProfile
import json
import secrets
import re
import time
from urllib.parse import parse_qs, urlparse


def _is_teacher(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile.is_teacher


def _serialize_participants(room):
    participants = room.participants.select_related("user", "user__userprofile").order_by("joined_at")
    return [
        {
            "username": participant.user.username,
            "is_creator": participant.user_id == room.creator_id,
            "role": participant.user.userprofile.role,
        }
        for participant in participants
    ]


def _broadcast_participants(room):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"room_{room.room_id}",
        {
            "type": "participants_update",
            "participants": _serialize_participants(room),
        },
    )


def _build_youtube_sync_payload(room):
    current_time = room.youtube_time or 0.0
    if room.youtube_state == "playing" and room.youtube_updated_at:
        current_time = max(
            0.0,
            current_time + (timezone.now() - room.youtube_updated_at).total_seconds(),
        )
    return {
        "type": "init",
        "videoId": room.youtube_video_id or "",
        "t": current_time,
        "state": room.youtube_state or "paused",
        "server_ts_ms": int(time.time() * 1000),
    }


def _build_whiteboard_payload(room):
    return {
        "image": room.whiteboard_data or "",
        "updated_at": int(room.whiteboard_updated_at.timestamp() * 1000) if room.whiteboard_updated_at else 0,
    }


@login_required
def participants_json(request, room_id):
    room = Room.objects.get(room_id=room_id)
    Participant.objects.get_or_create(room=room, user=request.user)
    return JsonResponse({"participants": _serialize_participants(room)})


@login_required
def youtube_sync_state(request, room_id):
    room = Room.objects.get(room_id=room_id)
    Participant.objects.get_or_create(room=room, user=request.user)

    if request.method == "GET":
        return JsonResponse(_build_youtube_sync_payload(room))

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "method_not_allowed"}, status=405)

    is_room_teacher = request.user == room.creator and _is_teacher(request.user)
    if not is_room_teacher:
        return JsonResponse({"ok": False, "error": "forbidden"}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)

    event_type = payload.get("type")
    now = timezone.now()

    if event_type == "set_video":
        video_id = (payload.get("videoId") or "").strip()
        if video_id:
            room.youtube_video_id = video_id
        room.youtube_state = "paused"
        room.youtube_time = float(payload.get("t", 0) or 0)
        room.youtube_updated_at = now
    elif event_type == "play":
        room.youtube_state = "playing"
        room.youtube_time = float(payload.get("t", 0) or 0)
        room.youtube_updated_at = now
    elif event_type == "pause":
        room.youtube_state = "paused"
        room.youtube_time = float(payload.get("t", 0) or 0)
        room.youtube_updated_at = now
    elif event_type == "seek":
        room.youtube_time = float(payload.get("t", 0) or 0)
        room.youtube_updated_at = now
    elif event_type == "sync":
        state = payload.get("state")
        if state in ("playing", "paused"):
            room.youtube_state = state
        room.youtube_time = float(payload.get("t", 0) or 0)
        room.youtube_updated_at = now
    elif event_type == "heartbeat":
        room.youtube_state = "playing"
        room.youtube_time = float(payload.get("t", 0) or 0)
        room.youtube_updated_at = now
    else:
        return JsonResponse({"ok": False, "error": "invalid_event"}, status=400)

    room.save(update_fields=["youtube_video_id", "youtube_state", "youtube_time", "youtube_updated_at"])
    return JsonResponse({"ok": True, "sync": _build_youtube_sync_payload(room)})


@login_required
def whiteboard_sync_state(request, room_id):
    room = Room.objects.get(room_id=room_id)
    Participant.objects.get_or_create(room=room, user=request.user)

    if request.method == "GET":
        return JsonResponse(_build_whiteboard_payload(room))

    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "method_not_allowed"}, status=405)

    is_room_teacher = request.user == room.creator and _is_teacher(request.user)
    if not is_room_teacher:
        return JsonResponse({"ok": False, "error": "forbidden"}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)

    image = str(payload.get("image", ""))
    room.whiteboard_data = image
    room.whiteboard_updated_at = timezone.now()
    room.save(update_fields=["whiteboard_data", "whiteboard_updated_at"])
    return JsonResponse({"ok": True, "whiteboard": _build_whiteboard_payload(room)})


def _extract_youtube_id(url: str) -> str:
    if not url:
        return ""
    url = url.strip()

    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url

    try:
        parsed = urlparse(url)
    except Exception:
        return ""

    host = (parsed.netloc or "").lower()
    path = (parsed.path or "").strip("/")

    if host in {"youtu.be", "www.youtu.be"} and path:
        candidate = path.split("/")[0]
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
            return candidate

    if host in {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtube-nocookie.com",
        "www.youtube-nocookie.com",
    }:
        video_id = parse_qs(parsed.query).get("v", [""])[0]
        if re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
            return video_id

        parts = [part for part in path.split("/") if part]
        if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live", "v"}:
            candidate = parts[1]
            if re.fullmatch(r"[A-Za-z0-9_-]{11}", candidate):
                return candidate

    m = re.search(r"youtu\.be/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

    m = re.search(r"[?&]v=([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

    m = re.search(r"/embed/([A-Za-z0-9_-]{6,})", url)
    if m:
        return m.group(1)

    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url

    return ""


@login_required
def create_room(request):
    if not _is_teacher(request.user):
        return render(
            request,
            "rooms/create_room.html",
            {"error": "Seul un professeur peut creer une room."},
            status=403,
        )

    room_id = secrets.token_hex(4)
    Room.objects.create(room_id=room_id, creator=request.user, mode="youtube")
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
    if room.mode != "youtube":
        room.mode = "youtube"
        room.save(update_fields=["mode"])

    Participant.objects.get_or_create(room=room, user=request.user)
    is_teacher = request.user == room.creator and _is_teacher(request.user)
    channel_layer = get_channel_layer()

    if request.method == "POST" and request.POST.get("youtube_url") is not None:
        if not is_teacher:
            participants = room.participants.select_related("user")
            room_messages = room.messages.select_related("user")
            return render(
                request,
                "rooms/room.html",
                {
                    "room": room,
                    "participants": participants,
                    "messages": room_messages,
                    "is_teacher": is_teacher,
                    "user_role": "professeur" if is_teacher else "eleve",
                    "error": "Seul un professeur peut modifier la video.",
                },
                status=403,
            )

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
                async_to_sync(channel_layer.group_send)(
                    f"youtube_{room_id}",
                    {"type": "youtube_event", "event": {"type": "set_video", "videoId": vid, "t": 0}},
                )

        if changed:
            room.save()

    participants = room.participants.select_related("user", "user__userprofile")
    messages = room.messages.select_related("user")

    _broadcast_participants(room)

    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_role = "professeur" if user_profile.is_teacher else "eleve"

    return render(
        request,
        "rooms/room.html",
        {
            "room": room,
            "participants": participants,
            "messages": messages,
            "is_teacher": is_teacher,
            "user_role": user_role,
        },
    )


@login_required
def leave_room(request, room_id):
    room = Room.objects.get(room_id=room_id)
    Participant.objects.filter(room=room, user=request.user).delete()
    _broadcast_participants(room)
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
