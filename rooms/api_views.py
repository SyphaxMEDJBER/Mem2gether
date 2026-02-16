import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import CourseNote, Room


def _parse_payload(request):
    if request.content_type and "application/json" in request.content_type:
        try:
            return json.loads(request.body.decode("utf-8") or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
    return request.POST


@login_required
@require_http_methods(["GET", "POST"])
def course_notes_api(request):
    if request.method == "POST":
        payload = _parse_payload(request)
        if payload is None:
            return JsonResponse({"error": "invalid_json"}, status=400)

        room_id = str(payload.get("room_id", "")).strip()
        content = str(payload.get("content", "")).strip()
        raw_timecode = payload.get("timecode")

        if not room_id:
            return JsonResponse({"error": "missing_room_id"}, status=400)
        if not content:
            return JsonResponse({"error": "missing_content"}, status=400)

        try:
            timecode = int(float(raw_timecode))
            if timecode < 0:
                raise ValueError
        except (TypeError, ValueError):
            return JsonResponse({"error": "invalid_timecode"}, status=400)

        try:
            room = Room.objects.get(room_id=room_id)
        except Room.DoesNotExist:
            return JsonResponse({"error": "room_not_found"}, status=404)

        note = CourseNote.objects.create(
            user=request.user,
            room=room,
            content=content,
            timecode=timecode,
        )

        return JsonResponse(
            {
                "id": note.id,
                "room_id": note.room.room_id,
                "user": note.user.username,
                "content": note.content,
                "timecode": note.timecode,
                "created_at": note.created_at.isoformat(),
            },
            status=201,
        )

    room_id = request.GET.get("room_id", "").strip()
    if not room_id:
        return JsonResponse({"error": "missing_room_id"}, status=400)

    notes = (
        CourseNote.objects.filter(room__room_id=room_id)
        .select_related("user")
        .order_by("timecode", "created_at")
    )

    return JsonResponse(
        {
            "room_id": room_id,
            "notes": [
                {
                    "id": note.id,
                    "user": note.user.username,
                    "content": note.content,
                    "timecode": note.timecode,
                    "created_at": note.created_at.isoformat(),
                }
                for note in notes
            ],
        }
    )
